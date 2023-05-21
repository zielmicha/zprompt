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
             (destination-dir (expand-file-name "~/var/zprompt/files"))
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
           (json-file (expand-file-name "~/var/zprompt/point.json"))
	   ;(inhibit-message t)
	   )
      (write-region json-data nil json-file nil 'inhibit-message))))
  
(add-hook 'post-command-hook 'zprompt/save-buffer)
(add-hook 'post-command-hook 'zprompt/save-point)

(defun zprompt/apply-expansion (result)
  "apply changes described from JSON"
  (let* ((prev-point (point))
	 (result-point (cdr (assoc 'point result)))
	 (result-text (cdr (assoc 'text result))))
    (goto-char result-point)
    (delete-region prev-point result-point)
    (insert result-text)))

(defun zprompt/prompt-expand ()
  (interactive)
  (zprompt/save-buffer)
  (zprompt/save-point)
  (let* ((shortcut (read-from-minibuffer "shortcut:"))
	 (result
	  (zprompt/run-and-parse-json "~/r/zprompt/expand.sh" shortcut)))
    (zprompt/apply-expansion result)))

;(cdr (assoc 'text (zprompt/run-and-parse-json "~/r/zprompt/expand.sh" "")))
;(my-prompt-expand)
(global-set-key (kbd "M-<return>") 'zprompt/prompt-expand)

(defun zprompt/insert-at (result)
  "apply changes described from JSON"
  (let* ((prev-point (point))
	 (result-point (cdr (assoc 'point result)))
	 (result-text (cdr (assoc 'text result))))
    (goto-char result-point)
    (insert result-text)))

(defun zprompt-exec ()
  (interactive)
  (zprompt/save-buffer)
  (zprompt/save-point)
  (let* ((result
	  (zprompt/run-and-parse-json "~/r/zprompt/exec.sh" ""))
	  (result-id (cdr (assoc 'launch-command result)))
	  )
    (zprompt/insert-at result)
    (zprompt/run-in-new-vterm
     result-id
     (format "~/r/zprompt/process-wrapper.sh %s" result-id))
    ))

(global-set-key (kbd "S-C-<return>") 'zprompt-exec)

(defun zprompt/run-in-new-vterm (filename command)
  (interactive "sCommand: ")
  (let* (
	 (vterm-shell command))
    (vterm-other-window)
    (set-visited-file-name filename)
    ))


(defun zprompt/vterm-after-exit (buf event)
  "Enables copy mode after process termination."
  (save-window-excursion
    (switch-to-buffer buf)
    (set-buffer-modified-p nil)
    (vterm-copy-mode 1)))

;(setq vterm-exit-functions nil)
(add-hook 'vterm-exit-functions 'zprompt/vterm-after-exit)

(require 'ansi-color)
(defun display-ansi-colors ()
  (interactive)
  (ansi-color-apply-on-region (point-min) (point-max)))

(setq vterm-copy-mode-remove-fake-newlines 't)
