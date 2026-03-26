"""Bridge para convertir Message PTB a formato interno."""

from typing import Any, Dict, List, Optional

try:
    from telegram import Message
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    Message = None


class MessageBridge:
    """Convierte Message de PTB a formato interno de la app."""
    
    @staticmethod
    def to_internal(message: Any) -> Dict[str, Any]:
        """Convierte Message PTB a diccionario interno.
        
        Args:
            message: Message de PTB
            
        Returns:
            Diccionario con formato interno
        """
        if not HAS_TELEGRAM or message is None:
            return {}
        
        from robot_ptb_compat.bridge.user_bridge import UserBridge
        from robot_ptb_compat.bridge.chat_bridge import ChatBridge
        
        result = {
            "message_id": message.message_id,
            "date": message.date.isoformat() if hasattr(message, 'date') and message.date else None,
        }
        
        if hasattr(message, 'from_user') and message.from_user:
            result["from"] = UserBridge.to_internal(message.from_user)
        
        if hasattr(message, 'chat') and message.chat:
            result["chat"] = ChatBridge.to_internal(message.chat)
        
        if hasattr(message, 'forward_from'):
            result["forward_from"] = UserBridge.to_internal(message.forward_from)
        
        if hasattr(message, 'forward_from_chat'):
            result["forward_from_chat"] = ChatBridge.to_internal(message.forward_from_chat)
        
        if hasattr(message, 'reply_to_message') and message.reply_to_message:
            result["reply_to_message"] = MessageBridge.to_internal(message.reply_to_message)
        
        if hasattr(message, 'text'):
            result["text"] = message.text
        
        if hasattr(message, 'entities'):
            result["entities"] = MessageBridge._entities_to_internal(message.entities)
        
        if hasattr(message, 'caption'):
            result["caption"] = message.caption
        
        if hasattr(message, 'photo'):
            result["photo"] = [MessageBridge._photo_to_internal(p) for p in message.photo] if message.photo else []
        
        if hasattr(message, 'document'):
            result["document"] = MessageBridge._document_to_internal(message.document)
        
        if hasattr(message, 'sticker'):
            result["sticker"] = MessageBridge._sticker_to_internal(message.sticker)
        
        if hasattr(message, 'video'):
            result["video"] = MessageBridge._video_to_internal(message.video)
        
        if hasattr(message, 'voice'):
            result["voice"] = MessageBridge._voice_to_internal(message.voice)
        
        if hasattr(message, 'audio'):
            result["audio"] = MessageBridge._audio_to_internal(message.audio)
        
        if hasattr(message, 'location'):
            result["location"] = MessageBridge._location_to_internal(message.location)
        
        if hasattr(message, 'venue'):
            result["venue"] = MessageBridge._venue_to_internal(message.venue)
        
        if hasattr(message, 'contact'):
            result["contact"] = MessageBridge._contact_to_internal(message.contact)
        
        if hasattr(message, 'invoice'):
            result["invoice"] = MessageBridge._invoice_to_internal(message.invoice)
        
        if hasattr(message, 'successful_payment'):
            result["successful_payment"] = MessageBridge._successful_payment_to_internal(message.successful_payment)
        
        if hasattr(message, 'callback_query'):
            result["callback_query"] = message.callback_query
        
        if hasattr(message, 'inline_keyboard_markup'):
            result["reply_markup"] = MessageBridge._keyboard_to_internal(message.inline_keyboard_markup)
        
        return result
    
    @staticmethod
    def _entities_to_internal(entities: List[Any]) -> List[Dict[str, Any]]:
        """Convierte MessageEntity list."""
        result = []
        for entity in entities:
            result.append({
                "type": entity.type,
                "offset": entity.offset,
                "length": entity.length,
                "url": entity.url if hasattr(entity, 'url') else None,
                "user": entity.user if hasattr(entity, 'user') else None,
            })
        return result
    
    @staticmethod
    def _photo_to_internal(photo: Any) -> Dict[str, Any]:
        """Convierte PhotoSize."""
        return {
            "file_id": photo.file_id,
            "file_unique_id": photo.file_unique_id,
            "width": photo.width,
            "height": photo.height,
            "file_size": photo.file_size if hasattr(photo, 'file_size') else None,
        }
    
    @staticmethod
    def _document_to_internal(doc: Any) -> Dict[str, Any]:
        """Convierte Document."""
        return {
            "file_id": doc.file_id,
            "file_unique_id": doc.file_unique_id,
            "file_name": doc.file_name if hasattr(doc, 'file_name') else None,
            "mime_type": doc.mime_type if hasattr(doc, 'mime_type') else None,
            "file_size": doc.file_size if hasattr(doc, 'file_size') else None,
        }
    
    @staticmethod
    def _sticker_to_internal(sticker: Any) -> Dict[str, Any]:
        """Convierte Sticker."""
        return {
            "file_id": sticker.file_id,
            "file_unique_id": sticker.file_unique_id,
            "width": sticker.width,
            "height": sticker.height,
            "is_animated": sticker.is_animated if hasattr(sticker, 'is_animated') else False,
            "is_video": sticker.is_video if hasattr(sticker, 'is_video') else False,
        }
    
    @staticmethod
    def _video_to_internal(video: Any) -> Dict[str, Any]:
        """Convierte Video."""
        return {
            "file_id": video.file_id,
            "file_unique_id": video.file_unique_id,
            "width": video.width,
            "height": video.height,
            "duration": video.duration,
            "mime_type": video.mime_type if hasattr(video, 'mime_type') else None,
        }
    
    @staticmethod
    def _voice_to_internal(voice: Any) -> Dict[str, Any]:
        """Convierte Voice."""
        return {
            "file_id": voice.file_id,
            "file_unique_id": voice.file_unique_id,
            "duration": voice.duration,
            "mime_type": voice.mime_type if hasattr(voice, 'mime_type') else None,
        }
    
    @staticmethod
    def _audio_to_internal(audio: Any) -> Dict[str, Any]:
        """Convierte Audio."""
        return {
            "file_id": audio.file_id,
            "file_unique_id": audio.file_unique_id,
            "duration": audio.duration,
            "performer": audio.performer if hasattr(audio, 'performer') else None,
            "title": audio.title if hasattr(audio, 'title') else None,
            "mime_type": audio.mime_type if hasattr(audio, 'mime_type') else None,
        }
    
    @staticmethod
    def _location_to_internal(location: Any) -> Dict[str, Any]:
        """Convierte Location."""
        return {
            "longitude": location.longitude,
            "latitude": location.latitude,
            "horizontal_accuracy": location.horizontal_accuracy if hasattr(location, 'horizontal_accuracy') else None,
            "live_period": location.live_period if hasattr(location, 'live_period') else None,
        }
    
    @staticmethod
    def _venue_to_internal(venue: Any) -> Dict[str, Any]:
        """Convierte Venue."""
        return {
            "location": MessageBridge._location_to_internal(venue.location),
            "title": venue.title,
            "address": venue.address,
            "foursquare_id": venue.foursquare_id if hasattr(venue, 'foursquare_id') else None,
        }
    
    @staticmethod
    def _contact_to_internal(contact: Any) -> Dict[str, Any]:
        """Convierte Contact."""
        return {
            "phone_number": contact.phone_number,
            "first_name": contact.first_name,
            "last_name": contact.last_name if hasattr(contact, 'last_name') else None,
            "user_id": contact.user_id if hasattr(contact, 'user_id') else None,
        }
    
    @staticmethod
    def _invoice_to_internal(invoice: Any) -> Dict[str, Any]:
        """Convierte Invoice."""
        return {
            "title": invoice.title,
            "description": invoice.description,
            "start_parameter": invoice.start_parameter,
            "currency": invoice.currency,
            "total_amount": invoice.total_amount,
        }
    
    @staticmethod
    def _successful_payment_to_internal(payment: Any) -> Dict[str, Any]:
        """Convierte SuccessfulPayment."""
        return {
            "currency": payment.currency,
            "total_amount": payment.total_amount,
            "invoice_payload": payment.invoice_payload,
            "telegram_payment_charge_id": payment.telegram_payment_charge_id if hasattr(payment, 'telegram_payment_charge_id') else None,
        }
    
    @staticmethod
    def _keyboard_to_internal(keyboard: Any) -> Dict[str, Any]:
        """Convierte InlineKeyboardMarkup."""
        if keyboard is None:
            return {}
        return {
            "inline_keyboard": [
                [
                    {
                        "text": button.text,
                        "callback_data": button.callback_data if hasattr(button, 'callback_data') else None,
                        "url": button.url if hasattr(button, 'url') else None,
                    }
                    for button in row
                ]
                for row in keyboard.inline_keyboard
            ]
        }


__all__ = ["MessageBridge"]
