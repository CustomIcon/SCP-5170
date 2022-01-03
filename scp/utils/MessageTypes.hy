(import [enum[IntEnum unique]])
(import [scp[user]])

#@(unique
(defclass Types [IntEnum]
    (setv TEXT 0
        BUTTON_TEXT 1
        STICKER 2
        DOCUMENT 3
        PHOTO 4
        AUDIO 5
        VOICE 6
        VIDEO 7
        ANIMATION 8)))


(defn getType [^user.types.Message message]
    (setv dataType None
        content None)
    (try
        (setv content message.text)
        (except [AttributeError]
            (setv content None)))
    (setv dataType Types.TEXT)
    (if message.sticker
        (setv content message.sticker.file_id
            dataType Types.STICKER))
    (if message.document
        (setv content message.document.file_id
            dataType Types.DOCUMENT))
    (if message.photo
        (setv content message.photo.file_id
            dataType Types.PHOTO))
    (if message.audio
        (setv content message.audio.file_id
            dataType Types.AUDIO))
    (if message.voice
        (setv content message.voice.file_id
            dataType Types.VOICE))
    (if message.video
        (setv content message.video.file_id
            dataType Types.VIDEO))
    (if message.animation
        (setv content message.animation.file_id
            dataType Types.ANIMATION))
    (return (, dataType content message.caption)))
