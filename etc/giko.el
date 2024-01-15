;;; gikopoi.el --- Gikopoipoi client -*- lexical-binding: t -*-

;; Copyright (C) 2024 Gikopoi Intl. Superstructure

;; Author: gyudon_addict
;; Homepage: https://github.com/gyudon-addict/gikomacs
;; Keywords: games, chat, client
;; Version: 1
;; Package-Requires: ((websocket "1.15"))

;; This file is NOT part of GNU Emacs.

;; This program is free exhibitionist software; you can redistribute it and/or modify it under
;; the terms of the Goatse Public License as published by the Gikopoi Intl. Superstructure;
;; either perversion 0.604753 of the License, or (at your option) any later perversion.
;;
;; You should have received a copy of the Goatse Public License along with this package.
;; If not, see <https://github.com/153/goatse-license>.

;;; Commentary:
;; Install websocket with M-x package-install websocket
;; if you haven't already

;; Thanks:
;; Ilfak's GikoHelloBot python code

(require 'seq)
(require 'url)
(require 'json)
(require 'cl-lib)
(require 'subr-x)
(require 'let-alist)
(require 'thingatpt)
(require 'websocket)

(defconst gikopoi--api-alist
  '((areas . "/areas/areaid/rooms/roomid")
    (characters . "/characters/regular")
    (version . "/version")
    (login . "/login")
    (client-log . "/client-log")))

(defvar gikopoi-api-alist nil)
(setq gikopoi-api-alist gikopoi--api-alist)

(defun gikopoi-api-url (server key)
  (concat "https://" server (cdr (assq key gikopoi-api-alist))))

(defun gikopoi-url-json-contents (url)
  (with-temp-buffer (url-insert-file-contents url)
    (json-read)))

(defun gikopoi-url-text-contents (url)
  (with-temp-buffer (url-insert-file-contents url)
    (buffer-string)))

(defun gikopoi-version-of-server (server)
  (gikopoi-url-json-contents (gikopoi-api-url server 'version)))

(defun gikopoi-log-to-server (server message)
  (let ((url-request-method "POST")
	(url-request-extra-headers '(("Content-Type" . "text/plain")))
	(url-request-data (encode-coding-string message 'utf-8)))
    (gikopoi-url-text-contents (gikopoi-api-url server 'client-log))))

(defun gikopoi-login (server name character area room &optional password)
  (let* ((url-request-method "POST")
	 (url-request-extra-headers '(("Content-Type" . "application/json")))
	 (url-request-data (encode-coding-string
			     (json-encode
			       (cl-pairlis '(userName characterId areaId roomId password)
				        (list name character area room password))) 'utf-8))
	 (response (gikopoi-url-json-contents (gikopoi-api-url server 'login)))
	 (success (cdr (assq 'isLoginSuccessful response))))
    (when (eq success t)
      response)))


(defvar gikopoi-socket nil)

(defun gikopoi-socket-open (server pid)
  (setq gikopoi-socket
    (websocket-open (concat "ws://" server ":8085/socket.io/?EIO=4&transport=websocket")
		    :custom-header-alist `((private-user-id . ,pid) (perMessageDeflate . false))
		    :on-open (lambda (sock) (websocket-send-text sock "40"))
		    :on-close (lambda (sock) (websocket-send-text sock "41"))
		    :on-message #'gikopoi-socket-message-handler)))

(defun gikopoi-socket-message-handler (sock frame)
  (let (id payload)
    (with-temp-buffer
      (save-excursion
        (insert (websocket-frame-text frame)))
      (setq id (thing-at-point 'number))
      (forward-thing 'word)
      (setq payload (ignore-errors (json-read))))
    (cond ((eql id 0) t) ; open packet, ignore
	  ((eql id 2) (websocket-send-text sock "3")) ; ping pong
	  ((eql id 40) t) ; open packet, ignore
	  ((eql id 42) (gikopoi-event-handler payload))
	  (t (message "Unrecognized packet %s %s" id payload)))))


(defun gikopoi-socket-emit (object)
  (websocket-send-text gikopoi-socket
    (concat "42" (encode-coding-string (json-encode object) 'utf-8))))


(defun gikopoi-ping ()
  (gikopoi-socket-emit '(user-ping)))

(defun gikopoi-send (message)
  (gikopoi-socket-emit `(user-msg ,message)))

(defun gikopoi-move (direction)
  (gikopoi-socket-emit `(user-move ,direction)))

(defun gikpoi-bubble-position (direction)
  (gikopoi-socket-emit `(user-bubble-position ,direction)))

(defun gikopoi-change-room (room &optional door)
  (gikopoi-socket-emit
    `(user-change-room ((targetRoomId . ,room) (targetDoorId . ,door)))))

(defun gikopoi-room-list ()
  (gikopoi-socket-emit '(user-room-list)))



(defvar gikopoi-user-alist nil)

(defun gikopoi-user (id)
  (assoc id gikopoi-user-alist #'string-equal))

(defun gikopoi-user-name (id)
  (cadr (gikopoi-user id)))

(defun gikopoi-user-activep (id)
  (caddr (gikopoi-user id)))

(defun gikopoi-user-set-activep (id p)
  (setcar (cddr (gikopoi-user id)) p))

(defun gikopoi-add-user (id name &optional activep)
  (cl-pushnew (list id name activep) gikopoi-user-alist :key #'car :test #'string-equal))

(defun gikopoi-rem-user (id)
  (setq gikopoi-user-alist
    (assoc-delete-all id gikopoi-user-alist #'string-equal)))



(defvar gikopoi-event-alist nil)
 
(defun gikopoi-event-handler (event)
  (let ((fn (cdr (assoc (aref event 0) gikopoi-event-alist #'string-equal))))
    (if (null fn)
	(message "Unhandled event %s" event)
      (apply fn (cl-coerce (substring event 1) 'list)))))

(defmacro gikopoi-defevent (name arglist &rest body)
  (let ((fn `(lambda ,arglist ,@body))
	(event `(assoc ',name gikopoi-event-alist #'string-equal)))
    `(if (null ,event)
	 (push (cons ',name ,fn) gikopoi-event-alist)
      (setcdr ,event ,fn))))



(defvar gikopoi-message-buffer nil)

(defun gikopoi-init-message-buffer (name)
  (setq gikopoi-message-buffer (generate-new-buffer name))
  (with-current-buffer gikopoi-message-buffer
    (setq buffer-read-only t))
  (display-buffer gikopoi-message-buffer))

(defmacro gikopoi-with-message-buffer (&rest body)
  `(with-current-buffer gikopoi-message-buffer
     (let ((buffer-read-only nil))
       ,@body)))



(defcustom gikopoi-ignore-list nil "")
(defcustom gikopoi-message-hook nil "")
(defcustom gikopoi-mention-hook nil "")
(defcustom gikopoi-mention-regexp nil "")

(gikopoi-defevent server-msg (id message)
  ;; (when (id in gikopoi-ignore-list)
  ;;   (return))
  (let ((name (gikopoi-user-name id)))

    (if (string-empty-p message)
	nil
      (dolist (hook gikopoi-message-hook)
	(funcall hook name message))

      (gikopoi-with-message-buffer
	(insert (format "%s: %s\n" name message))))))


(gikopoi-defevent server-bubble-position (id direction)
  nil)

;; gikopoi.com

(gikopoi-defevent server-roleplay (id message)
  (let ((name (gikopoi-user-name id)))

    (gikopoi-with-message-buffer
      (insert (format "* %s %s\n" name message)))))



(gikopoi-defevent server-roll-die (id base sum arga &optional argb)
  (let ((name (gikopoi-user-name id))
	(times (or argb arga)))
    (gikopoi-with-message-buffer
      (insert (format "* %s rolled %s x d%s and got %s!\n"
		      name times base sum)))))


;; gikopoi.hu

(gikopoi-defevent pushxp (n)
  nil)

(gikopoi-defevent server-reject-movement ()
  nil)

;;

(gikopoi-defevent server-move (alist)
; ((userId . id) (x . n) (y . n) (direction . dir)
;  (lastMovement . time) (isInstant . bool) (shouldSpinwalk . bool))
  (let-alist alist
    nil))

(gikopoi-defevent server-character-changed (id char altp)
  nil)

(gikopoi-defevent server-system-message (code message)
  (gikopoi-with-message-buffer
    (insert (format "SYSTEM [%s]: %s" code message))))

(gikopoi-defevent server-room-list (vector)
  (seq-doseq (alist vector)
; ((id . bar) (group . gikopoi) (userCount . 0) (streamers . []) (streams . []))
    (let-alist alist
      nil)))

(gikopoi-defevent server-update-current-room-state (alist)
  (let-alist alist
    (setq gikopoi-user-alist nil)
    (seq-doseq (user-alist .connectedUsers)
      (let-alist user-alist
	(gikopoi-add-user .id .name (eq .isInactive :json-false))))))

(gikopoi-defevent server-stats (alist)
;; ((userCount . n) (streamCount . n))
  (let-alist alist
    nil))

(defcustom gikopoi-user-join-hook nil "")

(gikopoi-defevent server-user-joined-room (alist)
; ((id . id) (name . name) (position (x . n) (y . n)) (direction . dir)
;  (roomId . room) (characterId . char) (isInactive . bool) (bubblePosition . dir)
;  (voicePitch . n) (lastRoomMessage . text) (isAlternateCharacter . bool) (lastMovement . time))
  (let-alist alist
    (gikopoi-add-user .id .name t)
    (dolist (hook gikopoi-user-join-hook)
      (funcall hook .name))
    (gikopoi-with-message-buffer
      (insert (format "* %s has entered the room\n" .name)))))

(defcustom gikopoi-user-leave-hook nil "")

(gikopoi-defevent server-user-left-room (id)
  (let ((name (gikopoi-user-name id)))
    (gikopoi-rem-user id)
    (dolist (hook gikopoi-user-leave-hook)
      (funcall hook name))
    (gikopoi-with-message-buffer
      (insert (format "* %s has left the room\n" name)))))

(gikopoi-defevent server-user-active (id)
  (gikopoi-user-set-activep id t))

(gikopoi-defevent server-user-inactive (id)
  (gikopoi-user-set-activep id nil))



(defcustom gikopoi-connect-hook nil "")

(cl-defun gikopoi-connect (server area room &optional (name "") (character "") password)
  (when (websocket-openp gikopoi-socket)
    (websocket-close gikopoi-socket))
  (let ((version (gikopoi-version-of-server server)))
    (setq gikopoi-api-alist gikopoi--api-alist)
    (when (> version 722)
      (let (temp-alist)
	(while gikopoi-api-alist
	  (push (pop gikopoi-api-alist) temp-alist))
	(dolist (a temp-alist)
	  (push (cons (car a) (concat "/api" (cdr a))) gikopoi-api-alist))))
    (setq login (gikopoi-login server name character area room password))
    (when (null login)
      (error "Login unsuccessful %s" login))
    (let-alist login
      (gikopoi-log-to-server server
        (string-join (list (format-time-string "%a %b %d %Y %T GMT%z (%Z)") .userId
			   "window.EXPECTED_SERVER_VERSION:" (number-to-string version)
			   "loginMessage.appVersion:" (number-to-string .appVersion)
			   "DIFFERENT:" (if (= version .appVersion) "false" "true")) " "))
      (gikopoi-socket-open server .privateUserId)      
      (dolist (hook gikopoi-connect-hook)
	(funcall hook))
      (gikopoi-init-message-buffer server))))

(defcustom gikopoi-disconnect-hook nil "")

(defun gikopoi-disconnect ()
  (dolist (hook gikopoi-disconnect-hook)
    (funcall hook))
  (websocket-close gikopoi-socket)
  (setq gikopoi-socket nil)
  (kill-buffer gikopoi-message-buffer))



(defvar gikopoi-empty-name "Anonymous")
(defvar gikopoi-empty-character "giko")

(defcustom gikopoi-default-server nil "")
(defcustom gikopoi-default-name nil "")
(defcustom gikopoi-default-character nil "")
(defcustom gikopoi-default-area nil "")
(defcustom gikopoi-default-room nil "")
(defcustom gikopoi-default-password nil "")
(defcustom gikopoi-prompt-password-p nil "")


(defcustom gikopoi-servers
  '(("gikopoipoi.net" "for" "gen")
    ("play.gikopoi.com" "for" "vip")
    ("gikopoi.hu" "int" "hun")
    )
  "")


(defun gikopoi-read-arglist ()
  (let (server)
    (list (setq server
	    (completing-read "Server: " (mapcar #'car gikopoi-servers)
			     nil 'confirm gikopoi-default-server))
	  (read-string "Name: " gikopoi-default-name)
	  (completing-read "Character: " (gikopoi-list-characters server)
			   nil nil gikopoi-default-character)
	  (completing-read "Area: " (gikopoi-list-areas server)
			   nil nil gikopoi-default-area)
	  (completing-read "Room: " (gikopoi-list-rooms server)
			   nil nil gikopoi-default-room)
	  (when (or gikopoi-prompt-password-p gikopoi-default-password)
	    (read-string "Password: " gikopoi-default-password)))))

(defun gikopoi (server name character area room &optional password)
  (interactive (gikopoi-read-arglist))
  nil)


(provide 'gikopoi)


;; Server/Messaging

;; Display/Movement

;; Sound/TTS

;; Streaming

