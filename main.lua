-- main.lua
local mp = require('mp')
local utils = require('mp.utils')
local options = require('mp.options')

local o = {
    script_dir = mp.get_script_directory(),
    key_toggle = 'n',
}
options.read_options(o)

-- Small helper: is our labeled filter active?
local function loudnorm_active()
    -- query current AF chain (string)
    local af = mp.get_property_native("af")  -- object settings list
    -- 'af' is a list of table entries like {name="lavfi", label="ln", ...}
    if type(af) == "table" then
        for _,f in ipairs(af) do
            if f.label == "ln" then return true end
        end
    end
    return false
end

-- Apply loudnorm string returned by Python
local function apply_loudnorm(filter_str)
    if not filter_str or filter_str == "" then
        mp.osd_message("loudnorm: empty filter string")
        return
    end
    -- We label the filter as @ln so we can remove/update it later
    -- Python already returns "[loudnorm=...]" so we prefix lavfi=
    local chain = "@ln:lavfi=" .. filter_str
    mp.commandv("af", "set", chain)  -- rebuilds the chain immediately
    mp.osd_message("loudnorm applied")
end

-- Remove our labeled filter
local function remove_loudnorm()
    mp.commandv("af", "remove", "@ln")
    mp.osd_message("loudnorm removed")
end

local ov -- overlay handle

local function run_python_and_apply()
    -- Toggle behavior: if active, remove and return
    if loudnorm_active() then
        remove_loudnorm()
        return
    end

    local path = mp.get_property("path")
    if not path then
        mp.osd_message("No file loaded")
        return
    end

    -- OSD: show we're working
    ov = mp.create_osd_overlay("ass-events")
    ov.data = "{\\an5}{\\b1}{\\fs20}Running LoudNorm analysis..."
    ov:update()

    -- Call Python via mpv subprocess API (safe quoting)
    local py = utils.join_path(o.script_dir, "loud_norm.py")
    local res = mp.command_native({
        name = "subprocess",
        playback_only = false,
        capture_stdout = true,
        capture_stderr = true,
        args = { "python3", py, path },
    })

    if ov then ov:remove() end

    if not res or res.status ~= 0 then
        local err = res and (res.stderr or res.stdout) or "unknown error"
        mp.msg.error("loudnorm subprocess failed: " .. err)
        mp.osd_message("loudnorm failed (see log)")
        return
    end

    -- Python prints something like: [loudnorm=I=...:...,...optional aresample...]
    local filter_str = (res.stdout or ""):gsub("%s+$", "")
    apply_loudnorm(filter_str)
end

-- Key to toggle
mp.add_key_binding(o.key_toggle, "toggle-loudnorm", run_python_and_apply)

-- Optional: auto-apply on open (uncomment if you prefer that behavior)
-- mp.register_event("file-loaded", run_python_and_apply)
