### Macro Triangle v2
### Charles M. Greenspon - charles.greenspon@gmail.com
### Thanks to Attilio Caravelli
# Import Pandas & numpy
import numpy as np
import pandas as pd
# Import Bokeh
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import layout, widgetbox, column, row, Spacer
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.io import show, export_png
from bokeh.models import Text, CDSView, Plot, Circle, CustomJS, CustomJSFilter, HoverTool, ColumnDataSource, Select, CategoricalColorMapper, TextInput
from bokeh.transform import factor_cmap
from bokeh.models.widgets import Toggle
from bokeh.events import ButtonClick
   
output_file("2D_MacroCompare.html", title="Macronutrient Comparison")
source_colors = pd.DataFrame()
source_colors['reg'] = ['#4CAF50', '#FF9800', '#9C27B0',  '#8D6E63', '#f44336', '#2196F3'] # Regular colors
source_colors['cb'] = ['#673AB7', '#FF5722', '#FFC107', '#3F51B5', '#f44336', '#2196F3'] 

# Prepare Data - Edit these columns if different/more/less are desired
target_cols = ['Food Group', 'Food Name', 'Protein (g)', 'Fat (g)', 'Carbohydrates (g)', 'Calories', 'Water (g)', 'Sugar (g)', 'Fiber (g)']
og_data = pd.read_excel("USDA-SR28-V1.xlsx", skiprows = 2, header = 1, usecols = target_cols)

groups_of_interest = ['Dairy and Egg Products','Beef Products', 'Breakfast Cereals',
                      'Cereal Grains and Pasta', 'Finfish and Shellfish Products',
                      'Fruits and Fruit Juices', 'Lamb, Veal, and Game Products',
                      'Legumes and Legume Products', 'Nut and Seed Products',
                      'Pork Products', 'Poultry Products', 'Sausages and Luncheon Meats',
                      'Vegetables and Vegetable Products']
trunc_data = og_data.loc[og_data['Food Group'].isin(groups_of_interest)]
trunc_data = trunc_data.reset_index(drop=True)

### Data Preparation
output_groups = ['Fruit & Vegetables', 'Cereals & Grains', 'Animal Products',
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

trunc_data['Meta Group'] = ""
trunc_data['def_colors'] = ""
trunc_data['cb_colors'] = ""
for g in range(len(output_groups)):
    trunc_data["Meta Group"].loc[trunc_data["Food Group"].str.contains('|'.join(meta_groups[g]))] = output_groups[g]
    trunc_data["def_colors"].loc[trunc_data["Food Group"].str.contains('|'.join(meta_groups[g]))] = source_colors.loc[g,'reg']
    trunc_data["cb_colors"].loc[trunc_data["Food Group"].str.contains('|'.join(meta_groups[g]))] = source_colors.loc[g,'cb']
    
trunc_data['x'] = trunc_data['Calories']
trunc_data['y'] = trunc_data['Protein (g)']
trunc_data['color'] = trunc_data["def_colors"]

# Prepare the legend
legend_x = np.ones(len(output_groups)) * 1000
legend_y = np.linspace(100,80,6)
legend_c = {'reg': source_colors['reg'].to_list(), 'cb': source_colors['cb'].to_list()}
legend_source = ColumnDataSource(dict(x=legend_x, y=legend_y, text=output_groups, colors=legend_c['reg']))
legend_glyph = Text(x="x", y="y", text="text", text_align="right", text_color="colors", text_font_size = "10pt")

### Search filter
unfilt_source = ColumnDataSource(trunc_data)
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

food_search = TextInput(value="", name='foodSearchTxtInput', title="Food Search:", callback=callback, width=200)

custom_filter = CustomJSFilter(args=dict(source=unfilt_source, sel=filtered_source), code='''
    return sel.data['x'];
''')
view = CDSView(source=unfilt_source, filters=[custom_filter])

# Colorblind toggle
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

color_toggle = Toggle(label="Colorblind Mode", button_type="success", callback = clr_callback, width=200)

### Plotting
p_tools = "hover, wheel_zoom, box_zoom, reset"
p = figure(title = "Amount per 100g", tools = p_tools, plot_width=900,
           x_range=(-50, 1050), x_axis_label='Calories',
           y_range=(-5,105), y_axis_label='Protein (g)', sizing_mode='scale_width')
    
p.circle(x = 'x', y = 'y', size = 7, color = 'color', alpha = 0.3,
         source = unfilt_source, view=view, name = 'dp')
p.add_glyph(legend_source, legend_glyph)


p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

p.hover.tooltips = [
    ("Name", "@{Food Name}")]
p.hover.names = ['dp']

### Make X/Y selection
callback_x = CustomJS(args=dict(source=unfilt_source, ax_lab=p.xaxis[0], ax_range=p.x_range,
                                leg_source=legend_source), code="""
        var selected_column = cb_obj.value
        // Set data
        var data = source.data;
        data['x'] = data[cb_obj.value];
        var leg_x = leg_source.data['x']
        // Edit axis label
        ax_lab.axis_label = cb_obj.value
        // Edit ranges
        if (cb_obj.value.includes('(g)')){
                ax_range.start = -5;
                ax_range.end = 105;
                for (var i = 0; i < 6; i++){
                        leg_x[i] = 100;
                }
        } else {
                ax_range.start = -50;
                ax_range.end = 1050;
                for (var i = 0; i < 6; i++){
                        leg_x[i] = 1000;
                }
        }
        // Push changes
        source.change.emit();
        ax_lab.change.emit();
        ax_range.change.emit();
        leg_source.change.emit();
""")
select_x = Select(title="X-Axis:", value="Calories", options=target_cols[2:len(target_cols)], callback=callback_x, width=200)

callback_y = CustomJS(args=dict(source=unfilt_source, ax_lab=p.yaxis[0], ax_range=p.y_range,
                                leg_source=legend_source, y_vals=legend_y), code="""
        var selected_column = cb_obj.value
        // Set data
        var data = source.data;
        data['y'] = data[cb_obj.value];
        var leg_y = leg_source.data['y']
        // Edit axis label
        ax_lab.axis_label = cb_obj.value
        // Edit axis range
        if (cb_obj.value.includes('(g)')){
                ax_range.start = -5;
                ax_range.end = 105;
                for (var i = 0; i < 6; i++){
                        leg_y[i] = y_vals[i];
                }
        } else {
                ax_range.start = -50;
                ax_range.end = 1050;
                for (var i = 0; i < 6; i++){
                        leg_y[i] = y_vals[i] * 10;
                }
        }
        // Push changes
        source.change.emit();
        ax_lab.change.emit();
        ax_range.change.emit();
        leg_source.change.emit();
""")
select_y = Select(title="Y-Axis:", value="Protein (g)", options=target_cols[2:len(target_cols)], callback=callback_y, width=200)

# Go
#show(row(column(food_search, select_x, select_y,color_toggle, inf) ,p))
show(column(row(Spacer(width=50),food_search, select_x, select_y,Spacer(width=20)) , row(p, Spacer(width=20)), row(Spacer(width=50),color_toggle,Spacer(width=500))))
#export_png(p, filename="plot.png")