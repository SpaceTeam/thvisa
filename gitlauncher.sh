#!/bin/bash
# Bash Menu Script Example
#https://askubuntu.com/questions/1705/how-can-i-create-a-select-menu-in-a-shell-script

# defines #
#use underscores in these options for better readability
o1="git-gui"
o2="git_change_user"
o3="Software_Update"
o4="Quit"
repo="/home/pi/testrig"

br="-----------------------------------------------------"
options=("$o1" "$o2" "$o3" "$o4") # insert option3 here if needed

function header
{
	cd $repo
	#clear
	echo $br
	olduser="$(git config --get user.name)"
	echo "git user: $olduser"
	echo $br
	echo "${options[@]}" # repeat options
}

function replacevariableinfile # variable file new
{
# $1 $2 are fct parameters
new="\"$3\"" # escape the strings
#replacelineafter
rpla="$1="
#replacewith
rpw="$rpla$new"
echo $new
echo $rpla
echo $rpw

# THIS ONLY WORKS WITH DOUBLE QUOTES
# SINGLE QUOTES sed ONLY IS GOOD FOR STRINGS
# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
sed -i "s,$rpla.*,$rpw," $2
}

# "main" #

header

# PS3: configures the "select" command
PS3='Please enter your choice: '

select opt in "${options[@]}"
do
    case $opt in
        "$o1")
            echo "you chose choice $REPLY which is $opt"
            LC_ALL=en_US.utf8 git gui

            header
            ;;

        "$o2")
            echo "you chose choice $REPLY which is $opt"

            cd $repo
            olduser="$(git config --get user.name)"
            oldmail="$(git config --get user.email)"

            echo "please type git username:"
            read gusername
            echo "please type git email:"
            read gemail

            rem="$(git config --get remote.origin.url)"
            #newurl="${rem/$olduser/$gusername}" this didn't work since its not a convention
            echo "old url : $rem"
            
            echo "what do you want to replace here?"
            read todo
            echo "with what?"
            read overwrite

            newurl="${rem/$todo/$overwrite}"
            
            #echo "(copy/paste using crtl+SHIFT+C/V in terminal)"
            #echo "a text window will open after you press enter"
            #read something
            #gedit
            #echo "please paste new url (editing is horrible here): "
            #read newurl
            
            echo ""
            echo "old user: $olduser"
            echo "old mail: $oldmail"
            echo "old url : $rem"
            echo ""
            echo "new user: $gusername"
            echo "new email: $gemail"
            echo "new url: $newurl"
            echo ""
            echo "Is this correct? press Enter to continue, or close window to abort"
            read something

            # set git credentials global and of this repo
            git config --global user.name $gusername
            git config --global user.email $gemail
            git config remote.origin.url $newurl
            
            # set string in sw_update
            # didn't work if thirschb was not last user :(
            #sed -i "s/$oldurl/$newurl/g" sw_update.sh
            
            #this only as an effect the first time around
            #placeholder="tobereplaced"
            # THE / AFTER s DID define its seperator
            #sed -i 's/$placeholder/$newurl/g' sw_update.sh
            # double quotes required to tell bash to interpret variable as variables
            #sed -i "s,$placeholder,$newurl,g" sw_update.sh

            #this is regular operation
            sed -i "s,$oldurl,$newurl,g" sw_update.sh # quotes outside url
            replacevariableinfile "gitrepo" "sw_update.sh" $newurl # variable file new
            header
            ;;

        "$o3")
            echo "you chose choice $REPLY which is $opt"
            #copy software update to desktop and run from there, close this one
            #since this script may be updated as well

            sw="sw_update.sh"
            sw1="$repo/$sw"
            desktopsw="/home/pi/Desktop/$sw"
            echo $sw1
            echo $desktopsw
            cp $sw1 $desktopsw # tested: force overwrite works without add. command
            echo "please run $sw"
            echo "after the successful software update, you will be prompted to delete it"
            read something

            header
            ;;

#
#        "$o5")
#            echo "you chose choice $REPLY which is $opt"
#            echo "tough luck, this is not implemented"

#            header
#            ;;

        "$o4")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
