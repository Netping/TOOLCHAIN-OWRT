bm_ipkg_builder.sh
==================
Usage: bm_ipkg_builder.sh <package directory>


"package directory" structure:

epic4_owrt_log
├── conffiles                        - list of config files that should be kept during package upgrade
├── control                          - package control file 
└── data                             - data directory for files which should be placed to target filesystem
    ├── etc
    │   ├── config
    │   │   └── journalconf
    │   └── netping_log
    │       ├── commands
    │       │   └── cmd_show.py
    │       ├── Configname
    │       ├── Help
    │       ├── journal_hash
    │       └── system_hash
    └── usr
        └── lib
            └── python3.7
                └── journal


See epic4_owrt_log/control file for package details