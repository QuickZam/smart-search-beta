# smart-search-beta
Beta version of smart search. 

## [**Streamlit app**](https://quickzam-smart-search-beta-app-c3dwlc.streamlitapp.com/)

```{ python silent}
from app import super, si, ci, pi, check_email, get_title_helper
from npdoc_to_md import render_md_from_obj_docstring 

print(render_md_from_obj_docstring(parse_text, 'app.super')) 
print('\n\n') 
print(render_md_from_obj_docstring(parse_text, 'app.si')) 

```

## RUNNING DOCKER FILE 

```python
docker build -t streamlit .

docker run -p 8501:8501 streamlit
```