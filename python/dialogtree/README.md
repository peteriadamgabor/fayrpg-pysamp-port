# PySAMP Dialog Tree

This module offers a solution for more complex dialog structures (e.g. bank system). It is equipped with many features to work with SAMP dialogs in a fast and comfortable way.

## Features

#### Attach custom variables to individual dialogs and or list items:  
`f"DBID: #dbid->{m_player.id}# | Name: {m_player.name}" for m_player in players`
This way the 'm_player.id' will be displayed in the dialog text.

But there is a way to make it not appear. Here the `m_player` is not will be generated.

`f"#dbid~>{m_player.id}# Name: {m_player.name}"`

#### Syntax:

`#varibale->{display_variable}#` I call this solution constructive.

`#varibale~>{variable}#` I call this solution destructive. I call this solution destructive. 
Since the variable will not appear in the dialog



#### Use custom variables: 
You can use the variables of a previous dialog in your current content as follows:

`f"Enter the user new money. Current: #user_data.money# Ft"`

#### Syntax:

`#node_name.variable#`

#### Paging: 

In case you want to display a large list, the module will automatically split it into pages that you can navigate between.


### In the debug.py file, you can find a short description of the operation and structure.