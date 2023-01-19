pl_nums2mask = r"""
{
  "name": "pl-nums2mask",
  "dock_image": "localhost/fnndsc/pl-nums2mask:dne",
  "public_repo": "https://github.com/FNNDSC/pl-nums2mask",
  "type": "ds",
  "parameters": [
    {
      "name": "value",
      "type": "str",
      "optional": false,
      "flag": "--value",
      "short_flag": "-w",
      "action": "store",
      "help": "Voxel values to include in mask as a comma-separated list",
      "default": null,
      "ui_exposed": true
    },
    {
      "name": "output_suffix",
      "type": "str",
      "optional": true,
      "flag": "--output-suffix",
      "short_flag": "-o",
      "action": "store",
      "help": "output file name suffix",
      "default": ".mask.mnc",
      "ui_exposed": true
    },
    {
      "name": "pattern",
      "type": "str",
      "optional": true,
      "flag": "--pattern",
      "short_flag": "-p",
      "action": "store",
      "help": "pattern for file names to include",
      "default": "**/*.mnc",
      "ui_exposed": true
    }
  ],
  "icon": "",
  "authors": "FNNDSC <dev@babyMRI.org>",
  "title": "Create Brain Mask from Segmentation",
  "category": "MRI Processing",
  "description": "Create brain mask from segmentation",
  "documentation": "https://github.com/FNNDSC/pl-nums2mask",
  "license": "MIT",
  "version": "1.0.0",
  "selfpath": "/opt/conda/bin",
  "selfexec": "nums2mask",
  "execshell": "/opt/conda/bin/python3.1",
  "min_number_of_workers": 1,
  "max_number_of_workers": 1,
  "min_memory_limit": "500Mi",
  "max_memory_limit": "",
  "min_cpu_limit": "1000m",
  "max_cpu_limit": "",
  "min_gpu_limit": 0,
  "max_gpu_limit": 0
}
"""
