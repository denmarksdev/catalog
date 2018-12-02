# Run a test server.
from app import app
from app.sample_data import create as create_data_sample
import os

create_data_sample(os.path.join(app.root_path, 'static'))

app.run(host='0.0.0.0', port=8080, debug=True)
