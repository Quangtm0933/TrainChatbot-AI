"""
Chatbot service for TrainChatbot.

Điều phối các module NLP, tra cứu dữ liệu,
quản lý ngữ cảnh và tạo câu trả lời cho người dùng (có tích hợp Gemini).
"""

from utils.intent_classifier import classify_intent
from utils.entity_extractor import extract_entities
from services.schedule_service import search_schedules
from utils.gemini_client import load_api_key, send_message


def format_schedule_results(results: list[dict]) -> str:
    """
    Chuyển kết quả tra cứu lịch tàu thành câu trả lời dễ đọc.
    """
    if not results:
        return (
            "Rất tiếc, tôi chưa tìm thấy chuyến tàu phù hợp "
            "với thông tin bạn cung cấp."
        )

    response = ["Tôi tìm thấy các chuyến tàu sau:\n"]
    for schedule in results:
        response.append(
            f"Tàu **{schedule['train_name']}**\n"
            f"- Ga đi: {schedule['departure_station']}\n"
            f"- Ga đến: {schedule['arrival_station']}\n"
            f"- Ngày đi: {schedule['travel_date']}\n"
            f"- Giờ khởi hành: {schedule['departure_time']}\n"
            f"- Giờ đến: {schedule['arrival_time']}\n"
        )
        if schedule["distance_km"] is not None:
            response.append(f"- Khoảng cách: {schedule['distance_km']} km\n")

        if schedule["prices"]:
            response.append("- Giá vé tham khảo:\n")
            for ticket in schedule["prices"]:
                response.append(f"  + {ticket['seat_type']}: {ticket['price']:,} VNĐ\n")
        else:
            response.append("- Chưa có thông tin giá vé.\n")
        response.append("\n")

    response.append(
        "*Lưu ý: Đây là dữ liệu mô phỏng phục vụ học tập, "
        "không phải lịch tàu thực tế.*"
    )
    return "".join(response)


def process_message(message: str, context: dict = None) -> dict:
    """
    Xử lý tin nhắn, có sử dụng bộ nhớ ngữ cảnh và gọi Gemini API khi cần.
    """
    if context is None:
        context = {}

    if not isinstance(message, str):
        raise TypeError("Tin nhắn phải là chuỗi.")

    message = message.strip()

    if not message:
        return {
            "intent": "other", "entities": {},
            "response": "Bạn hãy nhập câu hỏi để tôi hỗ trợ nhé.",
            "data": None, "needs_followup": True, "context": context
        }

    # Bước 1: Nhận diện ý định & Trích xuất thông tin
    intent = classify_intent(message)
    entities = extract_entities(message)

    # Bước 2: Cập nhật Ngữ Cảnh
    if entities.get("departure_station"):
        context["departure_station"] = entities["departure_station"]
    if entities.get("arrival_station"):
        context["arrival_station"] = entities["arrival_station"]
    if entities.get("travel_date"):
        context["travel_date"] = entities["travel_date"]

    has_extracted_info = any(entities.values())
    if intent == "other" and has_extracted_info:
        intent = "search_schedule"

    # Bước 3: Xử lý theo ý định
    if intent == "greeting":
        return {
            "intent": intent, "entities": entities,
            "response": "Xin chào! Tôi là chatbot hỗ trợ tư vấn lịch trình và tra cứu thông tin vé tàu. Bạn muốn đi từ ga nào đến ga nào?",
            "data": None, "needs_followup": False, "context": context
        }

    if intent in ("search_schedule", "ticket_price", "search_route"):
        departure = context.get("departure_station")
        arrival = context.get("arrival_station")
        travel_date = context.get("travel_date")

        if not departure or not arrival:
            missing_info = []
            if not departure: missing_info.append("ga đi")
            if not arrival: missing_info.append("ga đến")
            return {
                "intent": intent, "entities": entities,
                "response": f"Để tra cứu, bạn vui lòng cho tôi biết thêm {' và '.join(missing_info)} nhé.",
                "data": None, "needs_followup": True, "context": context
            }

        if not travel_date:
            return {
                "intent": intent, "entities": entities,
                "response": f"Bạn muốn đi từ {departure} đến {arrival} vào ngày nào? (VD: 20/12/2026)",
                "data": None, "needs_followup": True, "context": context
            }

        try:
            results = search_schedules(departure, arrival, travel_date)
            response = format_schedule_results(results)
            context["travel_date"] = None
            return {
                "intent": intent, "entities": entities,
                "response": response,
                "data": results, "needs_followup": False, "context": context
            }
        except (ValueError, TypeError) as error:
            return {
                "intent": intent, "entities": entities,
                "response": f"Thông tin chưa hợp lệ: {error}",
                "data": None, "needs_followup": True, "context": context
            }

    if intent == "travel_advice":
        api_key = load_api_key()
        if not api_key:
            return {
                "intent": intent, "entities": entities,
                "response": "Hệ thống AI hiện chưa được cấu hình. Tuy nhiên, tôi vẫn có thể giúp bạn tra cứu vé tàu. Bạn muốn đi đâu?",
                "data": None, "needs_followup": False, "context": context
            }
            
        # Prompt "nhập vai" để Gemini trả lời đúng chuẩn tư vấn viên
        system_prompt = (
            f"Bạn là một chuyên gia du lịch đường sắt Việt Nam. "
            f"Khách hàng vừa hỏi: '{message}'. "
            f"Hãy tư vấn du lịch thật thân thiện, truyền cảm hứng trong khoảng 3 đến 4 câu."
        )
        
        try:
            # Truyền mảng rỗng [] cho history vì context tra vé ta đang tự quản lý
            bot_reply = send_message(api_key, system_prompt, [])
            return {
                "intent": intent, "entities": entities,
                "response": bot_reply,
                "data": None, "needs_followup": False, "context": context
            }
        except Exception as e:
            return {
                "intent": intent, "entities": entities,
                "response": "Rất tiếc, AI tư vấn đang quá tải mạng. Nhưng Huế, Đà Nẵng, Nha Trang đều là những điểm đến tuyệt vời! Bạn muốn tìm vé tàu đi đâu?",
                "data": None, "needs_followup": False, "context": context
            }

    if intent == "ticket_policy":
        return {
            "intent": intent, "entities": entities,
            "response": "Hiện tại tôi chưa có dữ liệu quy định đổi/trả vé. Bạn vui lòng xem trên website chính thức của Đường sắt Việt Nam nhé.",
            "data": None, "needs_followup": False, "context": context
        }

    return {
        "intent": intent, "entities": entities,
        "response": "Tôi chưa hiểu rõ yêu cầu của bạn. Bạn có thể hỏi về lịch tàu, giá vé hoặc yêu cầu tư vấn du lịch nhé.",
        "data": None, "needs_followup": True, "context": context
    }