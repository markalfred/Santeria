================
MagicSublime
================

A Sublime Text 2 plugin for MEDITECH's Magic programming languages. Designed with the needs of Client/Service programmers in mind.


The Problem
===========

Eclipse works well as an IDE for developers working with the Magic languages, but it is cumbersome and does not provide all the tools necessary for debugging.

MagicSublime is an attempt to provide debugging tools for Client/Service programmers in a sleek and beautiful way.


Getting Started
===============

MagicSublime is meant to be used alongside SVN. With SVN, you can download your entire application's latest code to your client.

- Install Sublime SVN from http://wbond.net/sublime_packages/svn

- Once installed, Checkout your application via the `SVN: Checkout` menu item.
	 To access:
	 - Press `Ctrl + Shift + P`
	 - Select `SVN: Checkout`
	 - Example Repository URL: `https://vcfs01.meditech.com/svn/CS-NPR/5.6.5/Source/ADM/`

- Install MagicSublime


How to Use
==========

In a Magic source code file, place your cursor on a bit of code and press F1. What occurs depends on what you have selected:

- Macro Call - Jumps to the macro definition.

- Macro Title - Jumps back to the call, or finds the first call in the file.

- Data Element / NPR Macro - Shows documentation on that item.

- Local Variable - Shows in-procedure documentation for that variable if it exists.

- Procedure Call - Procedure opens in a new tab.

----------

The Magic command can be mapped to any key.
`{ "keys": ["f1"], "command": "magic" }`