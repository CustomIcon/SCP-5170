(defn name_check [^str username]
    (return (lif username (+ "@" username) None)))


(defn bool_check [^bool var]
    (return (lif var "✅" "❌")))
