import os
from dotenv import load_dotenv
load_dotenv()


token = str(os.getenv("token1"))
admin_id = str(os.getenv("admin_id1"))
admin_ids = [admin_id]

print(type(admin_ids))
print(admin_ids)