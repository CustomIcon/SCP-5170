(import base64)
(import struct)
(import [attrify[Attrify]])


(defn unpackInlineMessage [^str inline_message_id]
    (setv temp {}
        (, dc_id message_id chat_id query_id)
            (struct.unpack "<iiiq"
                (base64.urlsafe_b64decode
                    (* (+ inline_message_id "=")
                    (% (len inline_message_id)  4)))))
    (setv chat_id (str chat_id)
        chat_id (chat_id.replace "-1" "-1001"))
    (assoc temp "dc_id" dc_id
        "message_id" message_id
        "chat_id" (int chat_id)
        "query_id" query_id
        "inline_message_id" inline_message_id)
    (return (Attrify temp)))
