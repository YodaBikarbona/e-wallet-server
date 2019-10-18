import platform
import pdfkit
import os
import subprocess


def _get_pdfkit_config():
    """wkhtmltopdf lives and functions differently depending on Windows or Linux. We
     need to support both since we develop on windows but deploy on Heroku.

    Returns:
        A pdfkit configuration
    """
    if platform.system() == 'Windows':
        return pdfkit.configuration(
            wkhtmltopdf=os.environ.get('WKHTMLTOPDF_BINARY', 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
    else:
        WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')],
                                           stdout=subprocess.PIPE).communicate()[0].strip()
        return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)
