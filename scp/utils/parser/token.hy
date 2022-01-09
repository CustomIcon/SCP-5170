(import re)

(defn tokenFetcher [^str token]
    (setv token (re.findall r"[0-9]{10}:[a-zA-Z0-9_-]{35}" token))
    (if (= (len token) 0)
        (return (, False False)))
    (return (, True (get token 0))))
