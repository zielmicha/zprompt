(require 'json)

(defun zprompt/run-and-parse-json (cmd args)
  (with-temp-buffer
    (call-process cmd nil (current-buffer) nil args)
    (goto-char (point-min))
    (json-read)))

;(zprompt/run-and-parse-json "echo" "[1,2]")

(defun zprompt/save-buffer ()
  (interactive)
  (when (buffer-file-name)
      (let* ((original-file-path (buffer-file-name))
             (hex-encoded-path (url-hexify-string original-file-path))
             (destination-dir (expand-file-name "~/var/emacs-state/files"))
             (destination-file (concat destination-dir "/" hex-encoded-path)))
	(if (< (point-max) 100000)
	    (write-region nil nil destination-file nil 'quiet)))))

(defun zprompt/save-point ()
  (interactive)
  (when (buffer-file-name)
    (let* ((buffer-name (buffer-file-name))
           (point (point))
           (data `((buffer . ,buffer-name) (point . ,point)))
           (json-data (json-serialize data :null-object nil :false-object :json-false))
           (json-file (expand-file-name "~/var/emacs-state/point.json"))
	   (inhibit-message t))
      (write-region json-data nil json-file))))
  
(add-hook 'post-command-hook 'zprompt/save-buffer)
(add-hook 'post-command-hook 'zprompt/save-point)

(defun zprompt/prompt-expand ()
  (interactive)
  (zprompt/save-buffer)
  (zprompt/save-point)
  (let* ((shortcut (read-from-minibuffer "shortcut:"))
	 (result
	  (zprompt/run-and-parse-json "~/r/zprompt/expand.sh" shortcut))

	 (prev-point (point))
	 (result-point (cdr (assoc 'point result)))
	 (result-text (cdr (assoc 'text result))))
    (message (format "completing: %s %s" result-point result-text))
    (goto-char result-point)
    (delete-region prev-point result-point)
    (insert result-text)
    ))

;(cdr (assoc 'text (zprompt/run-and-parse-json "~/r/zprompt/expand.sh" "")))
;(my-prompt-expand)
(global-set-key (kbd "M-<return>") 'zprompt/prompt-expand)
