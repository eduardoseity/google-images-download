import sys
import os
import argparse
import bs4
import pandas as pd
import pybase64
import magic
import mimetypes
import os
import urllib.request
import hashlib
from tqdm import tqdm

base_path = os.getcwd()
parser = argparse.ArgumentParser()
parser.add_argument('-i','--input',help='Set input .html file (ie: -i="index.html")',required=False,default='index.html')
parser.add_argument('-o','--output',help='Output folder to save the images (ie: -o="data/images")',required=False,default='dataset/images')

args = parser.parse_args()

def read_input(file:str) -> str:
    try:
        with open(file,'r') as f:
            html = f.read()
        return html
    except FileNotFoundError:
        print(f'File {args.input} not found!')
        exit()

def get_image_tags(html:str) -> list:
    src_list = []
    soup = bs4.BeautifulSoup(html, features='html.parser')
    html_div = soup.find('div', {'id':'islrg'})
    for tag in html_div.find_all('img'):
        try:
            src_list.append(tag['src'])
        except:
            pass
    return src_list

def get_df(src_list:[]) -> pd.DataFrame:
    df = pd.DataFrame({'src':src_list})
    df = df.drop_duplicates()
    df = df[df['src'].str.contains('favicon') == False]
    return df

def base64_to_image(base64:str,output_path:str):
    base64 = base64.split('base64')
    format = None
    if 'jpeg' in base64[0]:
        format = 'jpg'
    elif 'png' in base64[0]:
        format = 'png'
    elif 'gif' in base64[0]:
        format = 'gif'
    else:
        raise Exception('Unknown image extension')

    base64 = base64[1][1:]

    decoded_b64 = pybase64.b64decode((base64))
    file_name = f'{hashlib.md5(base64.encode()).hexdigest()}.{format}'
    file_path = os.path.join(output_path,file_name)
    img_file = open(file_path, 'wb')
    img_file.write(decoded_b64)
    img_file.close()

def url_to_image(url:str,output_path:str):
    mime = magic.Magic(mime=True)
    output = hashlib.md5(url.encode()).hexdigest()
    file_path = os.path.join(output_path,output)
    urllib.request.urlretrieve(url,file_path)
    mimes = mime.from_file(file_path)
    ext = mimetypes.guess_all_extensions(mimes)[0]
    os.rename(file_path, file_path+ext)

if __name__ == '__main__':
    output_path = os.path.join(base_path,args.output)
    if os.path.exists(output_path) == False:
        os.makedirs(output_path)
    
    html = read_input(os.path.join(base_path,args.input))
    src_list = get_image_tags(html)
    df = get_df(src_list)

    print()
    print('Saving the images. Please wait...')
    for row in tqdm(df.iterrows()):
        src = row[1]['src']
        if src[0:4] == 'data':
            base64_to_image(src,output_path)
        elif src[0:4] == 'http':
            url_to_image(src,output_path)
        else:
            raise Exception('Unknown source')
    print()
    print(f'Images saved successfully on {args.output}')
    print('Total:',df.shape[0],'images')