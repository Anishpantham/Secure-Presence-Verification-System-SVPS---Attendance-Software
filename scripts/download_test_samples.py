"""Fetch two public reference portraits for model smoke tests, not enrollment datasets."""
from pathlib import Path
import hashlib
import urllib.request

root=Path(__file__).resolve().parents[1]/'.runtime'
root.mkdir(exist_ok=True)
samples={
 'astronaut.png':('https://raw.githubusercontent.com/scikit-image/scikit-image/v0.24.0/skimage/data/astronaut.png','88431cd9653ccd539741b555fb0a46b61558b301d4110412b5bc28b5e3ea6cb5'),
 'grace_hopper.jpg':('https://raw.githubusercontent.com/matplotlib/matplotlib/v3.9.2/lib/matplotlib/mpl-data/sample_data/grace_hopper.jpg','a8ca6d734765703b09728ab47fe59f473d93ae3967fc24c7c0288c3c7adb7130'),
}
for name,(url,expected) in samples.items():
 path=root/name
 if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==expected:
  print('Verified',name)
  continue
 with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
 if hashlib.sha256(data).hexdigest()!=expected:raise RuntimeError('Reference image checksum mismatch')
 path.write_bytes(data)
 print('Downloaded and verified',name)
