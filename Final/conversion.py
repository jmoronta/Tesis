from aspose.imaging import *
from aspose.imaging.fileformats.tiff.enums import *
from aspose.imaging.fileformats.jpeg2000 import *
from aspose.imaging.fileformats.png import *
from aspose.imaging.imageoptions import *
from aspose.pycore import is_assignable
import os


if 'TEMPLATE_DIR' in os.environ:
	templates_folder = os.environ['TEMPLATE_DIR']
else:
	templates_folder = r"/home/kbza/Proyectos/Final/templates"

delete_output = 'SAVE_OUTPUT' not in os.environ

data_dir = templates_folder


def process_convertion():
	import_formats, export_formats = get_available_image_formats()
	
	for import_key, import_value in import_formats.items():
		format_ext = import_key
		input_file = os.path.join(templates_folder, f"template.{format_ext}")
		
		if not os.path.exists(input_file):
			continue
		
		for export_key, export_value in export_formats.items():
			output_file = os.path.join(templates_folder, f"convert-{format_ext}-to-{export_key}.{export_key}")
			print("Processing conversion:" + output_file)
			with Image.load(input_file) as image:
				export_options = export_value.clone()
				if is_assignable(image, VectorImage):
					rasterization_options = import_value
					rasterization_options.page_width = float(image.width)
					rasterization_options.page_height = float(image.height)
					export_options.vector_rasterization_options = rasterization_options

				image.save(output_file, export_options)

			if delete_output:
				os.remove(output_file)


def get_available_image_formats():
	obj_init = Jpeg2000Options()
	obj_init.codec = Jpeg2000Codec.J2K
	obj_init2 = Jpeg2000Options()
	obj_init2.codec = Jpeg2000Codec.JP2
	obj_init3 = PngOptions()
	obj_init3.color_type = PngColorType.TRUECOLOR_WITH_ALPHA
	obj_init4 = {}
	obj_init4["bmp"] = BmpOptions()
	obj_init4["gif"] = GifOptions()
	obj_init4["dicom"] = DicomOptions()
	obj_init4["jpg"] = JpegOptions()
	obj_init4["jpeg"] = JpegOptions()
	obj_init4["jpeg2000"] = Jpeg2000Options()
	obj_init4["j2k"] = obj_init
	obj_init4["jp2"] = obj_init2
	obj_init4["png"] = obj_init3
	obj_init4["apng"] = ApngOptions()
	obj_init4["tiff"] = TiffOptions(TiffExpectedFormat.DEFAULT)
	obj_init4["tif"] = TiffOptions(TiffExpectedFormat.DEFAULT)
	obj_init4["tga"] = TgaOptions()
	obj_init4["webp"] = WebPOptions()
	obj_init4["ico"] = IcoOptions(FileFormat.PNG, 24)
	raster_formats_that_support_export_and_import = obj_init4
	
	obj_init5 = EmfOptions()
	obj_init5.compress = True
	obj_init6 = WmfOptions()
	obj_init6.compress = True
	obj_init7 = SvgOptions()
	obj_init7.compress = True
	obj_init8 = {}
	obj_init8["emf"] = (EmfOptions(), EmfRasterizationOptions())
	obj_init8["svg"] = (SvgOptions(), SvgRasterizationOptions())
	obj_init8["wmf"] = (WmfOptions(), WmfRasterizationOptions())
	obj_init8["emz"] = (obj_init5, EmfRasterizationOptions())
	obj_init8["wmz"] = (obj_init6, WmfRasterizationOptions())
	obj_init8["svgz"] = (obj_init7, SvgRasterizationOptions())
	vector_formats_that_support_export_and_import = obj_init8
	
	obj_init9 = DxfOptions()
	obj_init9.text_as_lines = True
	obj_init9.convert_text_beziers = True
	obj_init10 = {}
	obj_init10["psd"] = PsdOptions()
	obj_init10["dxf"] = obj_init9
	obj_init10["pdf"] = PdfOptions()
	obj_init10["html"] = Html5CanvasOptions()
	formats_only_for_export = obj_init10
	
	obj_init11 = {}
	obj_init11["djvu"] = None
	obj_init11["dng"] = None
	obj_init11["dib"] = None
	formats_only_for_import = obj_init11
	
	obj_init12 = {}
	obj_init12["eps"] = EpsRasterizationOptions()
	obj_init12["cdr"] = CdrRasterizationOptions()
	obj_init12["cmx"] = CmxRasterizationOptions()
	obj_init12["otg"] = OtgRasterizationOptions()
	obj_init12["odg"] = OdgRasterizationOptions()
	vector_formats_only_for_import = obj_init12
	
	# Get total set of formats to what we can export images
	export_formats = {k: v[0] for k, v in vector_formats_that_support_export_and_import.items()}
	export_formats.update(formats_only_for_export)
	export_formats.update(raster_formats_that_support_export_and_import)
	
	# Get total set of formats that can be loaded
	import_formats = {k : VectorRasterizationOptions() for k in formats_only_for_import}
	import_formats.update(vector_formats_only_for_import)
	import_formats.update({k : v[1] for k, v in vector_formats_that_support_export_and_import.items()})
	
	return import_formats, export_formats


# run
process_convertion()