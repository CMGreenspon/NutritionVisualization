%%% 2D Macro Comparison (Animation)
%%% Charles M. Greenspon - charles.greenspon@gmail.com
%%% https://github.com/CMGreenspon/NutritionVisualization
%%% https://www.greenspon.science/nutrition
cd('C:\Users\somlab\Google Drive\Other\Visualizations\Nutrition\2DMacroCompare')
data = readtable('USDA-SR28-V1.xlsx', 'Range', 'A4:U6351');
data = data(:,[2,4,5,6,8,16,19,21]);

%% Prepare Data
list_of_groups = unique(data.FoodGroup);
goi = []; ind = 1;
for i = [3,5:7,9:16,21]
    goi{ind,1} = list_of_groups{i};
    ind = ind + 1;
end

for i = 1:height(data)
    logit(i) = any(strcmp(data.FoodGroup{i}, goi));
end

fdb = data(logit,:);
num_items = height(fdb);
% Data cleaning
fdb.Calories = fdb.Calories ./ 10; % Let calories be in the same range
fdb.Sugar_g_ = str2double(fdb.Sugar_g_); % Convert to double
fdb.Fiber_g_ = str2double(fdb.Fiber_g_); % Convert to double
% Add a blank column at the end to finish on
fdb.blank = ones(height(fdb), 1) * 50;
column_labels = {'', 'Protein', 'Fat', 'Carbohydrates', 'Calories', 'Water', 'Sugar', 'Fiber'};

%% Make supergroups
metagroup_labels = [{'Fruit & Vegetables'}, {'Cereals & Grains'}, {'Animal Products'}, {'Nuts & Seeds'}, {'Meat'}, {'Fish'}];
% Fruit & Veg
metagroup{1} = [{'Fruits and Fruit Juices'}, {'Vegetables and Vegetable Products'}, {'Legumes and Legume Products'}];
% Cereal and Grains
metagroup{2} = [{'Breakfast Cereals'}, {'Cereal Grains and Pasta'},{'Baked Products'}];
% Animal Products
metagroup{3} = [{'Dairy and Egg Products'}];
% Nuts & Seeds
metagroup{4} = [{'Nut and Seed Products'}];
% Meat
metagroup{5} = [{'Beef Products'}, {'Lamb, Veal, and Game Products'}, {'Pork Products'}, {'Poultry Products'}, {'Sausages and Luncheon Meats'}];
% Fish
metagroup{6} = [{'Finfish and Shellfish Products'}];

colors = [76, 175, 80; 255, 152, 0; 156, 39, 176; 141, 110, 99; 244, 67, 54; 33, 150, 243] ./ 255; % Assign color for each metagroup
color_vals = zeros([num_items, 3]);

% For each metagroup overwrite the foodgroup value
for mg = 1:length(metagroup)
    group_labels = metagroup{mg}; % Get list of labels
    mg_ind = ismember(fdb.FoodGroup(:),group_labels); % Get index of matching items
    fdb.FoodGroup(mg_ind) = {metagroup_labels{mg}}; % Overwrite value
    color_vals(mg_ind,:) = repmat(colors(mg,:),sum(mg_ind),1); % Assign appropriate color value to index (helps with expediting plotting)
end

%% Make transitions
mode = 'Video'; % Options: 'Test', 'Video'
transition_order = [3,5; 6,5; 6,2; 4,2; 7,2; 7,3; 2,3; 9,9]; % Pairs of columns in the database to plot x,y
transition_time = 3; % seconds
pause_time = 1.5; % seconds

% Legend text
leg_str = [];
for i = 1:length(metagroup)
    leg_str = [leg_str; {['\color[rgb]{', num2str(colors(i,:)), '}',  metagroup_labels{i}]}];
end
% Initialize all data at 0,0
[x_source, y_source] = deal(ones(num_items,1).*50);

% Make the figure
f = figure('Color', 'w'); 
axes('XCol', [1,1,1], 'YCol', [1 1 1]); hold on
h = scatter(x_source, y_source, 12, 'CData', color_vals,'MarkerFaceColor', 'flat', 'MarkerFaceAlpha', 0.2, 'MarkerEdgeAlpha', 0.2);
xlim([-5 105]); ylim([-5 105])
h.XDataSource = 'x_source'; % Link data
h.YDataSource = 'y_source';

% Blank labels to update
x_text = text(50, -5, '', 'VerticalAlignment', 'top', 'HorizontalAlignment', 'center', 'FontSize', 12, 'Color', [0.6 0.6 0.6]);
y_text = text(-5, 50, '', 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'center', 'Rotation', 90, 'FontSize', 11, 'Color', [0.6 0.6 0.6]);

% Make the necessary object
vidobj = []; % just because this needs to be passed to the update function
if strcmp(mode, 'Video')
    frame_rate = 60;
    transition_frames = frame_rate * transition_time;
    pause_frames = frame_rate * pause_time;
    leg_text = text(100,100, leg_str,'VerticalAlignment', 'top', 'HorizontalAlignment', 'right', 'FontSize', 12);
    vidobj = VideoWriter('MacroAnimation', 'MPEG-4');
    vidobj.FrameRate = frame_rate;
    vidobj.Quality = 100;
    open(vidobj);
    writeVideo(vidobj,getframe(gcf));
end

% Start the animation
for transition = 1:size(transition_order,1)
    x_interp = NaN(num_items,transition_frames); % Make empty array
    x_interp(:,1) = x_source; x_interp(:,end) = fdb{:,transition_order(transition,1)}; % Get first and last points
    x_interp = fillmissing(x_interp', 'linear')'; % Interpolate
    % Same for y
    y_interp = NaN(num_items,transition_frames);
    y_interp(:,1) = y_source; y_interp(:,end) = fdb{:,transition_order(transition,2)};
    y_interp = fillmissing(y_interp', 'linear')';
    for int = 1:transition_frames
        x_source = x_interp(:,int);
        y_source = y_interp(:,int);
        if int == round(transition_frames/2) % Update labels half way through the transition
            if transition < size(transition_order,1)
                x_text.String = column_labels{transition_order(transition,1)};
                y_text.String = column_labels{transition_order(transition,2)};
            else
                x_text.String = '';
                y_text.String = '';
            end
        end
        refreshdata % Push updates to the graph
        save_gcf(mode, vidobj)
    end

    for int = 1:pause_frames
        save_gcf(mode, vidobj)
    end

end

close(vidobj);

%% Update function
function save_gcf(mode, vidobj)
        if strcmp(mode, 'Test')
            pause(0.001)
        elseif strcmp(mode, 'Video')
            writeVideo(vidobj,getframe(gcf));
        end
end