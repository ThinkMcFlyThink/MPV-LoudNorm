-- main.lua
local mp = require('mp')
local options = require('mp.options')

local o = {
	script_dir = mp.get_script_directory(), -- get the dir of this script
	key_toggle = 'n',
}
options.read_options(o)

function run_python()
    -- This function uses python to do the dirty work as I don't know LUA
    -- Python spits out the filter and we grab it

    local path = mp.get_property("path")
    local pypath = 'python "'..o.script_dir..'/loud_norm.py" "'..path..'"'

    -- Display message to show that LoudNorm is running
    ov = mp.create_osd_overlay("ass-events")
    ov.data = "{\\an5}{\\b1}{\\fs20}Running LoudNorm... Please be patient."
    ov:update()

    -- Call Python to run FFMPEG & grab the printed message
    local handle = io.popen('python3 "'..o.script_dir..'/loud_norm.py" "'..path..'"')
    local result = handle:read("*all")
    handle:close()

    -- Clear loading message
    ov:remove()

    -- tell mpv to add/toggle the calculated loudnorm filter
    mp.command('no-osd af toggle lavfi='..result)
end

-- This is if we want to run script on open.
-- mp.add_hook("on_load", 500, on_load)

mp.add_key_binding(o.key_toggle, "toggle-loudnorm", run_python)
