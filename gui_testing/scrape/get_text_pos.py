import easyocr
import pandas as pd

# setting, use English and enable the combination of characters and numbers
reader = easyocr.Reader(['en']) # be able to use CUDA, much faster than CPU
allow_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '

screenshot_list = ['analysis', 'client_info', 'equipment_info', 'homepage', 'save']

for image in screenshot_list:
  result = reader.readtext(f'page_screenshots/{image}.png', detail=1, allowlist = allow_list)
      
  df = pd.DataFrame(result) # convert to 
  df.columns = ['pos', 'string', 'confidence']
  df.to_csv(f'data/{image}.csv', index=False)

