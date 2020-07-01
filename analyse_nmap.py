import re

def getIp(scan_report):
    """
    Return the first string who match with an IP pattern in scan_report
    """
    ip = 'no_ip' # Warning if there is no IP in the scan_report
    if search := re.search(r"(\d{1,3}\.?){4}", scan_report):
        ip = search.group()
    return ip

def getHostname(scan_report):
    """
    Return hostname from the first string who match with the hostname.sdis57.fr pattern in scan_report
    """
    hostname = 'no_name'
    if search := re.search(r"([a-zA-Z0-9_.-]*)\.sdis57\.fr", scan_report):
        hostname = search.group(1)
    return hostname

def getOs(scan_report):
    """
    Return os from the first string who match with the osfamily="os" pattern in scan_report
    """
    os = 'no_os'
    if search := re.search(r"osfamily=\"([a-zA-Z0-9_.-]*)\"", scan_report):
        os = search.group(1)
    return os

def extractNmapInfo(verbose=True, path=''):
    # Open and read nmap.xml
    try:
        nmap_xml = open(path, 'r')
        nmap_result = nmap_xml.read()
        nmap_xml.close()
    except Exception as e:
        print(e)
        return []

    # Read all beetween <host starttime=\"[0-9]+\" endtime=\"[0-9]+\"> and </host> beacons and push it to scan_reports list
    scan_reports = re.findall(r'<host starttime=\"[0-9]+\" endtime=\"[0-9]+\">([\s\S]*?)</host>', nmap_result)

    extracted_info = []

    for scan_report in scan_reports:
        # Get the IP address, hostname, and the OS for each machines detected by nmap
        ip = getIp(scan_report)
        hostname = getHostname(scan_report)
        os = getOs(scan_report)

        if verbose:
            print(ip, hostname, os)

        extracted_info.append((ip, hostname, os, ))

    return extracted_info