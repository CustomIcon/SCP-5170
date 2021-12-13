(import [pyrogram[types]])

(defn getAttr [^types.Message message ^list Attr]
    (for [attribute Attr]
        (setv attr (getattr message attribute))
        (if attr
            (return attr))))
