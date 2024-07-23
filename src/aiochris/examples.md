## Examples

#### Create a client given username and password

```python
from aiochris import ChrisClient

chris = await ChrisClient.from_login(
    url='https://cube.chrisproject.org/api/v1/',
    username='chris',
    password='chris1234'
)
```

#### Search for a plugin

```python
# it's recommended to specify plugin version
plugin = await chris.search_plugins(name_exact="pl-dcm2niix", version="0.1.0").get_only()

# but if you don't care about plugin version...
plugin = await chris.search_plugins(name_exact="pl-dcm2niix").first()
```

#### Create a feed by uploading a file

```python
uploaded_file = await chris.upload_file('./brain.nii', 'my_experiment/brain.nii')
dircopy = await chris.search_plugins(name_exact='pl-dircopy', version="2.1.1").get_only()
plinst = await dircopy.create_instance(dir=uploaded_file.parent)
feed = await plinst.get_feed()
await feed.set(name="An experiment on uploaded file brain.nii")
```

#### Run a *ds*-type *ChRIS* plugin

```python
# search for plugin to run
plugin = await chris.search_plugins(name_exact="pl-dcm2niix", version="0.1.0").get_only()

# search for parent node 
previous = await chris.plugin_instances(id=44).get_only()

await plugin.create_instance(
    previous=previous,               # required. alternatively, specify previous_id
    title="convert DICOM to NIFTI",  # optional
    compute_resource_name="galena",  # optional
    memory_limit="2000Mi",           # optional
    d=9,                             # optional parameter of pl-dcm2niix
)
```

#### Search for plugin instances

```python
finished_freesurfers = chris.plugin_instances(
    plugin_name_exact='pl-fshack',
    status='finishedSuccessfully'
)
async for p in finished_freesurfers:
    print(f'"{p.title}" finished on date: {p.end_date}')
```

#### Delete all plugin instances with a given title, in parallel

```python
import asyncio
from aiochris import ChrisClient, acollect

chris = ChrisClient.from_login(...)
search = chris.plugin_instances(title="delete me")
plugin_instances = await acollect(search)
await asyncio.gather(*(p.delete() for p in plugin_instances))
```

#### Enable Debug Logging

A log message will be printed to stderr before every HTTP request is sent.

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```
