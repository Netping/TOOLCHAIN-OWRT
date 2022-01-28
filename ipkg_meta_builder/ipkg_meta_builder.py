#!/usr/bin/python3
import sys
import re




def getValue(line, value):
    if line.upper().startswith(value):
        line = line[len(value):]
        #return with cut character '=' and '"''
        line = line[1:]
        #if exists '"' or "'" at the beginning and at the end of line then cut them too
        if (line[0] == '"' and line[len(line) - 1] == '"') or (line[0] == "'" and line[len(line) - 1] == "'"):
            line = line[1:]
            line = line[:-1]

        return line

    return ''

def writeControl(workdir, control_dict):
    try:
        if not control_dict['Depends']:
            control_dict['Depends'] = ' '

        with open(workdir + '/control', 'w') as f:
            f.write('Package: ' + control_dict['Package'] + '\n')
            f.write('Version: ' + control_dict['Version'] + '\n')
            f.write('Depends: ' + control_dict['Depends'] + '\n')
            f.write('License: ' + control_dict['License'] + '\n')
            f.write('Section: ' + control_dict['Section'] + '\n')
            f.write('Architecture: ' + control_dict['Architecture'] + '\n')
            f.write('Description: ' + control_dict['Description'] + '\n')

        print('File control created successfully!')
    except Exception as ex:
        print('File control creating failed! Reason: ' + str(ex))

def writeConffiles(workdir, confdir, conffiles_list):
    try:
        if confdir:
            if confdir[len(confdir) - 1] == '/':
                confdir = confdir[:-1]

        with open(workdir + '/conffiles', 'w') as f:
            for l in conffiles_list:
                f.write(confdir + '/' + l  + '\n')

        print('File conffiles created successfully!')
    except Exception as ex:
        print('File conffiles creating failed! Reason: ' + str(ex))

def printHelp(program):
    print('Usage: python3 ' + program + ' <arch> <path_to_dir> [output_path]')
    print('       Avail archs:')
    print('           x86-64')
    print('           arm_cortex-a7_neon-vfpv4')
    print('')
    print('       Documantation: https://netping.atlassian.net/wiki/spaces/NW/pages/3605266478/DOC2.TOOLCHAIN-OWRT.pkg+meta+builder')

if __name__ == "__main__":
    output_path = ''
    avail_archs = [ 'x86-64', 'arm_cortex-a7_neon-vfpv4' ]

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print('Error: wrong arguments!')
        printHelp(sys.argv[0])
        sys.exit(-1)

    if not sys.argv[1] in avail_archs:
        print('Error: wrong arguments!')
        printHelp(sys.argv[0])
        sys.exit(-2)        

    if len(sys.argv) == 4:
        output_path = sys.argv[3]

    try:
        conffiles = []
        confdir = ''
        control = {
                    'Package' : '',
                    'Version' : '',
                    'Depends' : '',
                    'License' : 'MIT',
                    'Section' : '',
                    'Category' : '',
                    'Architecture' : sys.argv[1],
                    'Description' : ''
                }
        with open(sys.argv[2] + '/Makefile.inf', 'r') as f:
            lines = f.readlines()

            for line in lines:
                line = line.strip()

                if not line:
                    continue
                    
                value = getValue(line, 'PKG_NAME')
                if value:
                    control['Package'] = value
                    continue

                value = getValue(line, 'PKG_VERSION')
                if value:
                    result = None
                    try:
                        result = re.findall(r'\S*\.V(\d+)\.S(\d+)', value)[0]
                    except:
                        result=re.findall(r'(\d+)\.(\d+)', value)[0]
                        
                    control['Version'] = result[0] + '.' + result[1] + control['Version']
                    continue

                value = getValue(line, 'PKG_RELEASE')
                if value:
                    control['Version'] = control['Version'] + '-' + value
                    continue

                value = getValue(line, 'PKG_DEPENDS')
                if value:
                    control['Depends'] = value
                    continue

                value = getValue(line, 'SECTION')
                if value:
                    control['Section'] = value
                    continue

                value = getValue(line, 'CATEGORY')
                if value:
                    control['Category'] = value
                    continue

                value = getValue(line, 'TITLE')
                if value:
                    control['Description'] = value
                    continue

                value = getValue(line, 'CONF_FILE')
                if value:
                    for e in value.split(' '):
                        conffiles.append(e)
                    continue

                value = getValue(line, 'CONF_FILES')
                if value:
                    for e in value.split(' '):
                        conffiles.append(e)
                    continue

                value = getValue(line, 'CONF_DIR')
                if value:
                    confdir = value
                    continue

        if not output_path:
            writeConffiles(sys.argv[2], confdir, conffiles)
            writeControl(sys.argv[2], control)
        else:
            writeConffiles(output_path, confdir, conffiles)
            writeControl(output_path, control)

    except Exception as ex:
        print('Error: exception ' + str(ex))
        sys.exit(-2)

    sys.exit(0)
