import webbrowser
import urllib.request
from bs4 import BeautifulSoup
try:
    import helpAbout,parameters
except ImportError:
    from COMTool import helpAbout,parameters


class AutoUpdate:
    updateUrl = "https://github.com/Sipeed/kflash_gui/releases"
    def detectNewVersion(self):
        """
        Determine if the current page is available.

        Args:
            self: (todo): write your description
        """
        try:
            page = urllib.request.urlopen(self.updateUrl)
            html_doc = page.read().decode()
            soup = BeautifulSoup(html_doc,"html.parser")
            for v in soup.select('.label-latest .css-truncate-target'):
                versionStr = v.get_text()
                version = list(map(int, versionStr[1:].split(".")))
                print("The latest is %s, now:V%d.%d.%d" %(versionStr,helpAbout.versionMajor,helpAbout.versionMinor, helpAbout.versionDev))
                if version[0]*10+version[1] > helpAbout.versionMajor*10+helpAbout.versionMinor:
                    return True
                return False
        except Exception as e:
            print("error:",e)
            return False
        print("Already latest version!")
        return False

    def OpenBrowser(self):
        """
        Opens the web browser.

        Args:
            self: (todo): write your description
        """
        webbrowser.open(self.updateUrl, new=0, autoraise=True)
        return