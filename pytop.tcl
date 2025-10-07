bind pub -|- !top pub:mtop
bind pub -|- !dtop pub:dtop

proc pub:dtop {nick output binary chan text} {
  global
  set binary {/glftpd/bin/pytop.py}
    foreach line [split [exec $binary "--day"] "\n"] {
       putquick "PRIVMSG $chan :$line"
    }
}
proc pub:mtop {nick output binary chan text} {
  global
  set binary {/glftpd/bin/pytop.py}
    foreach line [split [exec $binary "--month"] "\n"] {
       putquick "PRIVMSG $chan :$line"
    }
}
putlog "pytop loaded"
