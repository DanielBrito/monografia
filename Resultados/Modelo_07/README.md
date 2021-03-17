<h1 align="center">Modelo 07</h2>

<h2 align="center">📝 rules_7.slx</h2>

#### **_\#C1: Initial settings_**

_label = "building"; width = 10; depth = 15; height = 25;_

#### **_\#C2: Generating mass model_**

_{<> -> createShape("building", width, depth, height)};_

\# GRIDS:

#### **_\#C3: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_front"] > -> createGrid("main_front_grid", 25, 10)};_

#### **_\#C4: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_back"] > -> createGrid("main_back_grid", 25, 10)};_

#### **_\#C5: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_left"] > -> createGrid("main_left_grid", 25, 10)};_

#### **_\#C6: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_right"] > -> createGrid("main_right_grid", 25, 10)};_

\# FRONT DEFORMATION:

#### **_\#C7: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (23, 24, 25)] [colIdx in (3, 4, 5, 6, 7, 8)] [::groupRegions()] > -> addVolume("south_1", "building_front", 8, ["south_1_front", "south_1_left", "south_1_right"])};_

#### **_\#C8: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_1"] / [label=="south_1_front"] > -> roundShape("front", "outside", 0.2, 30, "main_front", "vertical")};_

#### **_\#C9: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22)] [colIdx in (3, 4, 5, 6, 7, 8)] [::groupRegions()] > -> addVolume("south_2", "building_front", 7, ["south_2_front", "south_2_left", "south_2_right"])};_

#### **_\#C10: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_2"] / [label=="south_2_front"] > -> roundShape("front", "outside", 0.2, 30, "main_front", "vertical")};_

#### **_\#C11: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (23, 24, 25)] [colIdx in (1, 2)] [::groupRegions()] > -> addVolume("south_4", "building_front", 6, ["south_4_front", "south_4_left", "south_4_right"])};_

#### **_\#C12: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (15, 16, 17, 18, 19, 20, 21, 22)] [colIdx in (1, 2)] [::groupRegions()] > -> addVolume("south_5", "building_front", 5, ["south_5_front", "south_5_left", "south_5_right"])};_

#### **_\#C13: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (23, 24, 25)] [colIdx in (9, 10)] [::groupRegions()] > -> addVolume("south_6", "building_front", 6, ["south_6_front", "south_6_left", "south_6_right"])};_

#### **_\#C14: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (15, 16, 17, 18, 19, 20, 21, 22)] [colIdx in (9, 10)] [::groupRegions()] > -> addVolume("south_7", "building_front", 5, ["south_7_front", "south_7_left", "south_7_right"])};_

\# RIGHT DEFORMATION:

#### **_\#C15: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (22, 23, 24, 25)] [colIdx in (1)] [::groupRegions()] > -> addVolume("east_1", "building_right", 6, ["east_1_front", "east_1_right", "east_1_right"])};_

#### **_\#C16: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_1"] / [label=="east_1_front"] > -> roundShape("front", "outside", 0.1, 30, "main_right", "vertical")};_

#### **_\#C17: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (22, 23, 24, 25)] [colIdx in (10)] [::groupRegions()] > -> addVolume("east_2", "building_right", 6, ["east_2_front", "east_2_right", "east_2_right"])};_

#### **_\#C18: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_2"] / [label=="east_2_front"] > -> roundShape("front", "outside", 0.1, 30, "main_right", "vertical")};_

#### **_\#C19: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (22, 23, 24, 25)] [colIdx in (2, 3, 4, 5, 6, 7, 8, 9)] [::groupRegions()] > -> addVolume("east_3", "building_right", 5, ["east_3_front", "east_3_right", "east_3_right"])};_

#### **_\#C20: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (19, 20, 21)] [colIdx in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)] [::groupRegions()] > -> addVolume("east_4", "building_right", 5, ["east_4_front", "east_4_right", "east_4_right"])};_

#### **_\#C21: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_4"] / [label=="east_4_front"] > -> roundShape("top", "outside", 0.1, 30, "main_right")};_

#### **_\#C22: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (10, 11, 12, 13, 14, 15, 16, 17, 18)] [colIdx in (1)] [::groupRegions()] > -> addVolume("east_5", "building_right", 3, ["east_5_front", "east_5_right", "east_5_right"])};_

#### **_\#C23: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_5"] / [label=="east_5_front"] > -> roundShape("front", "outside", 0.1, 30, "main_right", "vertical")};_

#### **_\#C24: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (10, 11, 12, 13, 14, 15, 16, 17, 18)] [colIdx in (10)] [::groupRegions()] > -> addVolume("east_6", "building_right", 3, ["east_6_front", "east_6_right", "east_6_right"])};_

#### **_\#C25: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_6"] / [label=="east_6_front"] > -> roundShape("front", "outside", 0.1, 30, "main_right", "vertical")};_

#### **_\#C26: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (10, 11, 12, 13, 14, 15, 16, 17, 18)] [colIdx in (2, 3, 4, 5, 6, 7, 8, 9)] [::groupRegions()] > -> addVolume("east_7", "building_right", 2, ["east_7_front", "east_7_right", "east_7_right"])};_

---

<h2 align="center">🏢 Resultado</h2>

<div align="center">
  <img src="modelo_07.png" alt="Modelo 07">
</div>
