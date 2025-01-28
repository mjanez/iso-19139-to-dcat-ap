import os
import tempfile
import logging
import yaml
from saxonche import PySaxonProcessor
from rdflib import Graph
from urllib.request import urlopen, urlretrieve
import ssl

# Load configuration from YAML file
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

# Extract URLs from configuration
XML_URL = config['xml_url']
XSL_URL = config['xsl_url']
LOCAL_XSL_PATH = os.path.join(os.path.dirname(__file__), "iso19139-to-geodcatap.xsl")

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class XSLTTransformer:
    """Class to handle XSLT transformations using SaxonC.

    Attributes:
        xslt_path (str): Path to the XSLT file.
        processor (PySaxonProcessor): SaxonC processor instance.
        xslt_processor (Xslt30Processor): SaxonC XSLT 3.0 processor instance.
    """

    def __init__(self, xslt_file):
        """Initializes the XSLTTransformer with the given XSLT file.

        Args:
            xslt_file (str): Path or URL to the XSLT file.

        Raises:
            FileNotFoundError: If the XSLT file does not exist.
        """
        log.debug("Initializing XSLTTransformer with xslt_file: %s", xslt_file)

        if xslt_file.startswith('http://') or xslt_file.startswith('https://'):
            self.xslt_path = LOCAL_XSL_PATH
            if not os.path.isfile(self.xslt_path):
                log.debug("Downloading XSLT file from URL: %s", xslt_file)
                urlretrieve(xslt_file, self.xslt_path)
        else:
            if not os.path.isfile(xslt_file):
                raise FileNotFoundError(f"The file {xslt_file} does not exist.")
            self.xslt_path = os.path.abspath(xslt_file)

        self.processor = PySaxonProcessor(license=False)
        self.xslt_processor = self.processor.new_xslt30_processor()

        log.debug("XSLTTransformer initialized successfully.")

    def transform(self, xml_data):
        """Transforms the given XML data using the XSLT file."""
        log.debug("Starting XML transformation.")
        try:
            if isinstance(xml_data, bytes):
                xml_data = xml_data.decode('utf-8')
    
            # Create output directory
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            os.makedirs(output_dir, exist_ok=True)
    
            # Save original XML content
            xml_file_path = os.path.join(output_dir, 'input_raw.xml')
            with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
                xml_file.write(xml_data)
    
            # Configure Saxon processor
            self.processor = PySaxonProcessor(license=False)
            self.xslt_processor = self.processor.new_xslt30_processor()
            
            # Set parameters to prevent URL resolution
            self.xslt_processor.set_parameter("resolve-external", self.processor.make_boolean_value(False))
            self.xslt_processor.set_cwd(os.path.dirname(self.xslt_path))
    
            # Create temporary file for transformation
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode='w', encoding='utf-8') as temp_file:
                temp_file.write(xml_data)
                temp_file_path = temp_file.name
    
            # Perform transformation with detailed logging
            log.debug(f"Starting XSLT transformation with:\n  Source: {temp_file_path}\n  XSLT: {self.xslt_path}")
            
            result = self.xslt_processor.transform_to_string(
                stylesheet_file=self.xslt_path,
                source_file=temp_file_path
            )
            
            # Add parameters to prevent URL resolution
            self.xslt_processor.set_parameter("resolve-external", self.processor.make_boolean_value(False))
            
            result = self.xslt_processor.transform_to_string(
                stylesheet_file=self.xslt_path,
                source_file=temp_file_path
            )
    
            if self.xslt_processor.exception_occurred:
                for error in self.xslt_processor.get_error_message():
                    log.error("Error in XSLT transformation: %s", error)
                raise RuntimeError("Error in XSLT transformation")
    
            # Save the result
            output_file_path = os.path.join(output_dir, 'transformed_output.rdf')
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(result)
    
            log.debug("XML transformation completed successfully. Result saved in %s", output_file_path)
            return result
    
        except Exception as e:
            log.error("Failed to transform XML content: %s", str(e))
            # Save error details for debugging
            error_path = os.path.join(output_dir, 'transformation_error.log')
            with open(error_path, 'w', encoding='utf-8') as error_file:
                error_file.write(f"Error: {str(e)}\n")
                error_file.write(f"XML content preview:\n{xml_data[:1000]}...")
            raise

# Create an unverified SSL context
context = ssl._create_unverified_context()

# Download and read the XML content
xml_content = urlopen(XML_URL, context=context).read()

# Initialize the XSLT transformer
transformer = XSLTTransformer(xslt_file=XSL_URL)

# Transform the XML content
rdf_result = transformer.transform(xml_content)