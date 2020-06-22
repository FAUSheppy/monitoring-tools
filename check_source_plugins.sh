#!/bin/bash
PLUGIN_NAME=Skillbird

/usr/local/bin/insurgency_rcon sm plugins list Skillbird | grep $PLUGIN_NAME &>/dev/null
ins01=$?
/usr/local/bin/insurgency_small_rcon sm plugins list Skillbird | grep $PLUGIN_NAME &>/dev/null
ins02=$?

if [ "$ins01" -ne "0" ]; then
	echo "Plugin not loaded!? (ins01)"
	exit 1;
fi

if [ "$ins02" -ne "0" ]; then
	echo "Plugin not loaded!? (ins02)"
	exit 1;
fi

echo "Plugin Loaded"
exit 0
