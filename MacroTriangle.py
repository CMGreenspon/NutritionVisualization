### Macro Triangle
### Charles M. Greenspon - charles.greenspon@gmail.com
### Thanks to Attilio Caravelli
# Import Pandas
import pandas as pd
# Import Bokeh
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import layout, widgetbox, column
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.io import show
from bokeh.models import Text, CDSView, Plot, Circle, CustomJS, CustomJSFilter, HoverTool, ColumnDataSource, Select, CategoricalColorMapper, TextInput
from bokeh.transform import factor_cmap
   
output_file("MacroTriangle.html", title="Macronutrient Proportions")

# Prepare Data
og_data = pd.read_csv("Food Database.csv")

groups_of_interest = ['Dairy and Egg Products', 'Fats and Oils',
                      'Baked Products', 'Beef Products', 'Breakfast Cereals',
                      'Cereal Grains and Pasta', 'Finfish and Shellfish Products',
                      'Fruits and Fruit Juices', 'Lamb, Veal, and Game Products',
                      'Legumes and Legume Products', 'Nut and Seed Products',
                      'Pork Products', 'Poultry Products', 'Sausages and Luncheon Meats',
                      'Snacks', 'Sweets', 'Vegetables and Vegetable Products']
trunc_data = og_data.loc[og_data['Food Group'].isin(groups_of_interest)]

trunc_data['sum'] = trunc_data[['Protein (g)','Carbohydrates (g)','Fat (g)']].sum(axis = 1)
trunc_data['pProtein'] = trunc_data['Protein (g)']/trunc_data['sum']
trunc_data['pCarbs'] = trunc_data['Carbohydrates (g)']/trunc_data['sum']
trunc_data['pFats'] = trunc_data['Fat (g)']/trunc_data['sum']
trunc_data['pCarb_pFats'] = trunc_data['pFats'] - trunc_data['pCarbs']

ratiod_data = trunc_data[['Food Group','Food Name','pCarb_pFats', 'pProtein']]

### Data Preparation
meta_sort = True

if meta_sort:
    output_groups = ['Fruit & Vegetables', 'Cereals & Grains', 'Animal Products',
                     'Nuts & Seeds', 'Meat', 'Fish']
    colors = ['#81C784', '#FFA000', '#E57373',  '#827717', '#D32F2F', '#0097A7']
              
    meta_groups = []
    meta_groups.append(['Fruits and Fruit Juices', 'Legumes and Legume Products',
                        'Vegetables and Vegetable Products']) # Fruit & Veg
    meta_groups.append(['Breakfast Cereals', 'Cereal Grains and Pasta']) # Cereals & Grains
    meta_groups.append(['Dairy and Egg Products']) # Animal Products
    meta_groups.append(['Nut and Seed Products']) # Nuts & Seeds
    meta_groups.append(['Beef Products', 'Lamb, Veal, and Game Products', 'Pork Products',
                     'Poultry Products', 'Sausages and Luncheon Meats']) # Meat
    meta_groups.append(['Finfish and Shellfish Products']) # Fish
    
    for g in range(len(output_groups)):
        ratiod_data["Food Group"].loc[ratiod_data["Food Group"].str.contains('|'.join(meta_groups[g]))] = output_groups[g]
    
    ratiod_data = ratiod_data.loc[ratiod_data['Food Group'].isin(output_groups)]

else:
    output_groups = groups_of_interest
    colors = ['#323232', '#311B92', '#BF360C', '#1B5E20', '#880E4F', '#01579B',
        '#9E9E9E', '#7B1FA2', '#FFA000', '#D32F2F', '#0097A7', '#BA68C8',
        '#FFB74D', '#81C784', '#E57373', '#64B5F6', '#827717', '#795548']

# Make data source
unfilt_source = ColumnDataSource(ratiod_data)

filterDataIndices = dict(x=[True for num in range(1, len(unfilt_source.data['Food Name']))])
           
filtered_source = ColumnDataSource(filterDataIndices)
    
callback = CustomJS(args=dict(source=filtered_source, sel=unfilt_source), code="""
        var textTyped = cb_obj.value.toUpperCase();
        var filteredDataSource = source.data['x'];
        for (var i = 0; i < sel.get_length(); i++){
            if (sel.data['Food Name'][i].toUpperCase().includes(textTyped)){
                filteredDataSource[i] = true;
            } else {
                filteredDataSource[i] = false;
            }
        }
        source.change.emit();
        sel.change.emit();
	""")

food_search = TextInput(value="", name='foodSearchTxtInput', title="Food Search:",sizing_mode='scale_width', callback=callback)

# The filter
custom_filter = CustomJSFilter(args=dict(source=unfilt_source, sel=filtered_source), code='''
    return sel.data['x'];
''')

view = CDSView(source=unfilt_source, filters=[custom_filter])

# Make the plot
p_tools = "hover, wheel_zoom, box_zoom, pan, reset"
p = figure(title = "Macronutrient Ratios", tools = p_tools, plot_width=800,
           plot_height=800, sizing_mode='scale_both', x_range=(-1.3, 1.3), y_range=(-0.2, 1.2))
p.hover.tooltips = [("Name", "@{Food Name}")]

p.circle(0, 0, size=0.00000001, color= "#ffffff", legend="Food Group")
for g in range(len(output_groups)):
    p.circle(0, 0, size=0.00000001, color= colors[g], legend=output_groups[g])
    
p.circle(x = 'pCarb_pFats', y = 'pProtein', size = 7,
         color = factor_cmap('Food Group', palette=colors, factors=output_groups),
         alpha = 0.3, source = unfilt_source, view=view)

p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.xaxis.visible = False
p.yaxis.visible = False

label_x = [-1.025, 0, 1.025]
label_y = [-0.05, 1.025, -0.05]
label_text = ['Carbohydrate', 'Protein', 'Fat']
label_source = ColumnDataSource(dict(x = label_x, y = label_y, text = label_text))
glyph = Text(x="x", y="y", text="text", text_align="center")
p.add_glyph(label_source, glyph)

p.legend.location = "top_right"
p.legend.border_line_alpha = 0

# Go
show(column(food_search, p)) 
#html = file_html(p, CDN, "my plot")
