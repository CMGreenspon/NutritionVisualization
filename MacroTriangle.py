### Macro Triangle v2
### Charles M. Greenspon - charles.greenspon@gmail.com
# Import Pandas & numpy
import numpy as np
import pandas as pd
# Import Bokeh
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import layout, widgetbox, column, row, Spacer
from bokeh.embed import file_html
from bokeh.io import show, output_notebook
from bokeh.models import Text, CDSView, Plot, Circle, CustomJS, CustomJSFilter, HoverTool, ColumnDataSource, Select, TextInput, TapTool
from bokeh.transform import factor_cmap
from bokeh.models.widgets import Toggle
from bokeh.events import ButtonClick
   
output_file("MacroTriangleV2.html", title="Macronutrient Proportions")
source_colors = pd.DataFrame()
source_colors['reg'] = ['#4CAF50', '#FF9800', '#9C27B0',  '#8D6E63', '#f44336', '#2196F3'] # Regular colors
source_colors['cb'] = ['#673AB7', '#FF5722', '#FFC107', '#3F51B5', '#f44336', '#2196F3'] 
# Prepare Data
og_data = pd.read_csv("Food Database.csv")

groups_of_interest = ['Dairy and Egg Products','Beef Products', 'Breakfast Cereals',
                      'Cereal Grains and Pasta', 'Finfish and Shellfish Products',
                      'Fruits and Fruit Juices', 'Lamb, Veal, and Game Products',
                      'Legumes and Legume Products', 'Nut and Seed Products',
                      'Pork Products', 'Poultry Products', 'Sausages and Luncheon Meats',
                      'Vegetables and Vegetable Products']
trunc_data = og_data.loc[og_data['Food Group'].isin(groups_of_interest)]

trunc_data['sum'] = trunc_data[['Protein (g)','Carbohydrates (g)','Fat (g)']].sum(axis = 1)
trunc_data['pProtein'] = trunc_data['Protein (g)']/trunc_data['sum']
trunc_data['pCarbs'] = trunc_data['Carbohydrates (g)']/trunc_data['sum']
trunc_data['pFats'] = trunc_data['Fat (g)']/trunc_data['sum']
trunc_data['pCarb_pFats'] = trunc_data['pFats'] - trunc_data['pCarbs']

ratiod_data = trunc_data[['Food Group','Food Name','pCarb_pFats', 'pProtein']]
ratiod_data = ratiod_data.reset_index(drop=True)

### Data Preparation
output_groups = ['Fruits & Vegetables', 'Cereals & Grains', 'Animal Products',
                 'Nuts & Seeds', 'Meat', 'Fish']          
meta_groups = []
meta_groups.append(['Fruits and Fruit Juices', 'Legumes and Legume Products',
                    'Vegetables and Vegetable Products']) # Fruit & Veg
meta_groups.append(['Breakfast Cereals', 'Cereal Grains and Pasta']) # Cereals & Grains
meta_groups.append(['Dairy and Egg Products']) # Animal Products
meta_groups.append(['Nut and Seed Products']) # Nuts & Seeds
meta_groups.append(['Beef Products', 'Lamb, Veal, and Game Products', 'Pork Products',
                 'Poultry Products', 'Sausages and Luncheon Meats']) # Meat
meta_groups.append(['Finfish and Shellfish Products']) # Fish

ratiod_data['Meta Group'] = ""
ratiod_data['def_colors'] = ""
ratiod_data['cb_colors'] = ""
for g in range(len(output_groups)):
    ratiod_data["Meta Group"].loc[ratiod_data["Food Group"].str.contains('|'.join(meta_groups[g]))] = output_groups[g]
    ratiod_data["def_colors"].loc[ratiod_data["Food Group"].str.contains('|'.join(meta_groups[g]))] = source_colors.loc[g,'reg']
    ratiod_data["cb_colors"].loc[ratiod_data["Food Group"].str.contains('|'.join(meta_groups[g]))] = source_colors.loc[g,'cb']
ratiod_data['color'] = ratiod_data["def_colors"]

# Prepare the legend
legend_x = np.ones(len(output_groups)) * -1
legend_y = np.linspace(0.975,0.8,6)
legend_c = {'reg': source_colors['reg'].to_list(), 'cb': source_colors['cb'].to_list()}
legend_source = ColumnDataSource(dict(x=legend_x, y=legend_y, text=output_groups, colors=legend_c['reg']))
legend_glyph = Text(x="x", y="y", text="text", text_align="left", text_color="colors", text_font_size = "10pt")

# Make seaschable data source
unfilt_source = ColumnDataSource(ratiod_data)
filterDataIndices = dict(x=[True for num in range(1, len(unfilt_source.data['Food Name']))])
filtered_source = ColumnDataSource(filterDataIndices)
    
callback = CustomJS(args=dict(source=filtered_source, sel=unfilt_source), code="""
        var textTyped = cb_obj.value.toUpperCase();
        var filteredDataSource = source.data['x'];
        for (var i = 0; i < sel.get_length(); i++){
            if (sel.data['Food Name'][i].toUpperCase().includes(textTyped)){
                    filteredDataSource[i] = true;
            } else if (sel.data['Food Group'][i].toUpperCase().includes(textTyped)){
                    filteredDataSource[i] = true;
            } else {
                    filteredDataSource[i] = false;
            }
        }
        source.change.emit();
        sel.change.emit();
	""")

food_search = TextInput(value="", name='foodSearchTxtInput', placeholder="Food Search:",
                        sizing_mode='scale_width', callback=callback, css_classes=["hide-label"])

custom_filter = CustomJSFilter(args=dict(source=unfilt_source, sel=filtered_source), code='''
    return sel.data['x'];
''')
view = CDSView(source=unfilt_source, filters=[custom_filter])

# Add toggle button for colorblind
clr_callback = CustomJS(args=dict(source=unfilt_source, color_source=legend_c,
                                  leg_source=legend_source), code="""
    var state = cb_obj.active
    var data = source.data
    var leg = leg_source.data
    if (state){
    data['color'] = data['cb_colors'];
    leg['colors'] = color_source['cb'];
    } else{
    data['color'] = data['def_colors'];
    leg['colors'] = color_source['reg'];
    }
    source.change.emit();
    leg_source.change.emit();    
    """)

color_toggle = Toggle(label="Colorblind Mode", button_type="success", callback = clr_callback)
             
# Make the plot
p_tools = "hover, wheel_zoom, pan, reset, tap"
p = figure(tools = p_tools, plot_width=775,toolbar_location ="below",
           plot_height=700, x_range=(-1.25, 1.25), y_range=(-0.1, 1.1))
#title = "Macronutrient Ratios", 
p.hover.tooltips = [("Name", "@{Food Name}")]
p.hover.names = ['dp']
p.add_glyph(legend_source, legend_glyph)
p.circle(x = 'pCarb_pFats', y = 'pProtein', size = 7,
         color = 'color', alpha = 0.3, source = unfilt_source, view=view,
         name='dp')

p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.xaxis.visible = False
p.yaxis.visible = False

label_x = [-1.025, 0, 1.025]
label_y = [-0.05, 1.025, -0.05]
label_text = ['Carbohydrate', 'Protein', 'Fat']
label_source = ColumnDataSource(dict(x = label_x, y = label_y, text = label_text))
label_glyph = Text(x="x", y="y", text="text", text_align="center")
p.add_glyph(label_source, label_glyph)

info_x = legend_x[0:2] * -1
info_y = legend_y[0:2]
info_text = ['Charles M. Greenspon', 'USDA/MyFoodData']
info_source = ColumnDataSource(dict(x = info_x, y = info_y, text = info_text))
info_glyph = Text(x="x", y="y", text="text", text_align="right", text_font_size = "10pt", text_color='#757575')
p.add_glyph(info_source, info_glyph, name='info')

tapback = CustomJS(code="""
    //console.log('x-position: ' + cb_obj.x)
    //console.log('y-position: ' + cb_obj.y)
    var x_pos = cb_obj.x
    var y_pos = cb_obj.y
    
    if (x_pos >= 0.6 && x_pos <= 1 && y_pos >= 0.975 && y_pos <= 1) {
    window.open("http://www.greenspon.science/home");
    } else if (x_pos >= 0.63 && x_pos <= 1 && y_pos >= 0.935 && y_pos <= 0.9565){
    window.open("https://tools.myfooddata.com/")
    }
""")

p.js_on_event('tap', tapback)

# Go
show(column(row(food_search, color_toggle), p))
