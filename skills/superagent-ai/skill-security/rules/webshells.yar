/*
    webshells.yar — webshell patterns in bundled source.
    Lineage: Neo23x0/signature-base, adapted for text/source scanning.
*/

rule php_webshell_eval_input
{
    meta:
        description = "PHP webshell — code execution on user-controlled superglobals"
        category = "webshell"
        severity = "CRITICAL"
        confidence = "0.85"
    strings:
        $eval_in   = /eval\s*\(\s*\$_(POST|GET|REQUEST|COOKIE|SERVER)\s*\[/ nocase
        $assert_in = /assert\s*\(\s*\$_(POST|GET|REQUEST|COOKIE)\s*\[/ nocase
        $sys_in    = /(system|shell_exec|passthru|popen|proc_open|exec)\s*\(\s*\$_(POST|GET|REQUEST)\s*\[/ nocase
        $preg_e    = /preg_replace\s*\(\s*["']\/.*\/e["']/ nocase
    condition:
        any of them
}

rule php_webshell_obfuscated
{
    meta:
        description = "Obfuscated PHP webshell — eval over decode chain"
        category = "webshell"
        severity = "CRITICAL"
        confidence = "0.8"
    strings:
        $b64_eval  = /eval\s*\(\s*base64_decode\s*\(/ nocase
        $gz_eval   = /eval\s*\(\s*gzinflate\s*\(\s*base64_decode/ nocase
        $rot_eval  = /eval\s*\(\s*str_rot13\s*\(/ nocase
        $gzun_eval = /eval\s*\(\s*gzuncompress\s*\(/ nocase
        $varfn     = /\$\w+\s*=\s*["'](system|exec|eval|assert)["']\s*;[^\n]{0,40}\$\w+\(/ nocase
    condition:
        any of them
}

rule script_webshell
{
    meta:
        description = "Python/JSP webshell — request param routed to command execution"
        category = "webshell"
        severity = "CRITICAL"
        confidence = "0.75"
    strings:
        $py_flask_cmd = /(request\.(args|form|values)\.get\([^)]*\))[^\n]{0,80}(os\.system|subprocess|popen)/ nocase
        $py_cgi_cmd   = /cgi\.FieldStorage\(\)[^\n]{0,120}(os\.system|subprocess|exec)/ nocase
        $jsp_runtime  = /Runtime\.getRuntime\(\)\.exec\([^)]*request\.getParameter/ nocase
    condition:
        any of them
}


/*
    cryptominers.yar — cryptojacking / mining indicators.
*/

rule cryptominer_indicators
{
    meta:
        description = "Cryptocurrency miner / cryptojacking indicators"
        category = "cryptominer"
        severity = "HIGH"
        confidence = "0.75"
    strings:
        $stratum    = /stratum\+tcp:\/\// nocase
        $xmrig      = /\bxmrig\b/ nocase
        $miner_pool = /(pool\.minexmr\.com|nanopool\.org|supportxmr\.com|f2pool\.com|nicehash)/ nocase
        $monero_cfg = /"(donate-level|rig-id|coin)"\s*:/ nocase
        $coinhive   = /(coinhive|cryptonight|randomx)/ nocase
        $wallet_arg = /--(donate-level|coin|url|user)\s+[^\s]{0,80}\.(xmr|monero)/ nocase
    condition:
        any of them
}


/*
    hacktools.yar — offensive tooling / exploit indicators.
*/

rule hacktool_indicators
{
    meta:
        description = "Offensive tools / recon / exploit frameworks"
        category = "hacktool"
        severity = "HIGH"
        confidence = "0.6"
    strings:
        $msf_payload = /(msfvenom|meterpreter|metasploit)\b/ nocase
        $mimikatz    = /(mimikatz|sekurlsa::|lsadump)/ nocase
        $recon       = /(nmap\s+-sS|masscan\b|gobuster\b|sqlmap\b)/ nocase
        $privesc     = /(linpeas|winpeas|GTFOBins|pwnkit|dirtycow)/ nocase
        $shellcode   = /\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){20,}/
    condition:
        any of them
}
