<h1 align="center">Modelo 11</h2>

<h2 align="center">📝 rules_11.slx</h2>

\# MIXING OUTSIDE AND INSIDE ROUNDING

#### **_\#C1: Initial settings_**

_label = "building"; width = 20; depth = 10; height = 5;_

#### **_\#C2: Generating mass model_**

_{<> -> createShape("building", width, depth, height)};_

\# GRIDS:

#### **_\#C3: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_front"] > -> createGrid("main_front_grid", 5, 20)};_

#### **_\#C4: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_back"] > -> createGrid("main_back_grid", 5, 20)};_

#### **_\#C5: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_left"] > -> createGrid("main_left_grid", 5, 10)};_

#### **_\#C6: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_right"] > -> createGrid("main_right_grid", 5, 10)};_

\# FRONT:

#### **_\#C7: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (1)] [::groupRegions()] > -> addVolume("south_1", "building_front", 1, ["south_1_front", "south_1_left", "south_1_right"])};_

#### **_\#C8: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_1"] / [label=="south_1_front"] > -> roundShape("left", "inside", 0.2, 30, "main_front", 0.05)};_

#### **_\#C9: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (2, 3, 4, 5, 6, 7)] [::groupRegions()] > -> addVolume("south_2", "building_front", 3, ["south_2_front", "south_2_left", "south_2_right"])};_

#### **_\#C10: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_2"] / [label=="south_2_front"] > -> roundShape("front", "outside", 0.3, 30, "main_front", "vertical")};_

#### **_\#C11: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (8, 9, 10)] [::groupRegions()] > -> addVolume("south_3", "building_front", 1, ["south_3_front", "south_3_left", "south_3_right"])};_

#### **_\#C12: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_3"] / [label=="south_3_front"] > -> roundShape("right", "inside", 0.4, 30, "main_front", 0.05)};_

#### **_\#C13: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (11, 12, 13)] [::groupRegions()] > -> addVolume("south_4", "building_front", 1, ["south_4_front", "south_4_left", "south_4_right"])};_

#### **_\#C14: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_4"] / [label=="south_4_front"] > -> roundShape("left", "inside", 0.4, 30, "main_front", 0.05)};_

#### **_\#C15: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (14, 15, 16, 17, 18, 19)] [::groupRegions()] > -> addVolume("south_5", "building_front", 3, ["south_5_front", "south_5_left", "south_5_right"])};_

#### **_\#C16: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_5"] / [label=="south_5_front"] > -> roundShape("front", "outside", 0.3, 30, "main_front", "vertical")};_

#### **_\#C17: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (20)] [::groupRegions()] > -> addVolume("south_6", "building_front", 1, ["south_6_front", "south_6_left", "south_6_right"])};_

#### **_\#C18: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_6"] / [label=="south_6_front"] > -> roundShape("right", "inside", 0.4, 30, "main_front", 0.05)};_

\# RIGHT:

#### **_\#C19: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (1)] [::groupRegions()] > -> addVolume("east_1", "building_right", 0.5, ["east_1_front", "east_1_left", "east_1_right"])};_

#### **_\#C20: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_1"] / [label=="east_1_front"] > -> roundShape("left", "inside", 0.2, 30, "main_right", 0.05)};_

#### **_\#C21: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (10)] [::groupRegions()] > -> addVolume("east_2", "building_right", 0.5, ["east_2_front", "east_2_left", "east_2_right"])};_

#### **_\#C22: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_2"] / [label=="east_2_front"] > -> roundShape("right", "inside", 0.2, 30, "main_right", 0.05)};_

#### **_\#C23: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (2, 3, 4, 5, 6, 7, 8, 9)] [::groupRegions()] > -> addVolume("east_3", "building_right", 3.5, ["east_3_front", "east_3_left", "east_3_right"])};_

#### **_\#C24: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_3"] / [label=="east_3_front"] > -> roundShape("front", "outside", 0.3, 30, "main_right", "vertical")};_

\# LEFT:

#### **_\#C25: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="main_left_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (1)] [::groupRegions()] > -> addVolume("west_1", "building_left", 0.5, ["west_1_front", "west_1_left", "west_1_right"])};_

#### **_\#C26: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="west_1"] / [label=="west_1_front"] > -> roundShape("left", "inside", 0.2, 30, "main_left", 0.05)};_

#### **_\#C27: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="main_left_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (10)] [::groupRegions()] > -> addVolume("west_2", "building_left", 0.5, ["west_2_front", "west_2_left", "west_2_right"])};_

#### **_\#C28: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="west_2"] / [label=="west_2_front"] > -> roundShape("right", "inside", 0.2, 30, "main_left", 0.05)};_

#### **_\#C29: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="main_left_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (2, 3, 4, 5, 6, 7, 8, 9)] [::groupRegions()] > -> addVolume("west_3", "building_left", 3.5, ["west_3_front", "west_3_left", "west_3_right"])};_

#### **_\#C30: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="west_3"] / [label=="west_3_front"] > -> roundShape("front", "outside", 0.3, 30, "main_left", "vertical")};_

\# BACK:

#### **_\#C31: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (1)] [::groupRegions()] > -> addVolume("north_1", "building_back", 1, ["north_1_front", "north_1_left", "north_1_right"])};_

#### **_\#C32: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_1"] / [label=="north_1_front"] > -> roundShape("left", "inside", 0.2, 30, "main_back", 0.05)};_

#### **_\#C33: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (2, 3, 4, 5, 6, 7)] [::groupRegions()] > -> addVolume("north_2", "building_back", 3, ["north_2_front", "north_2_left", "north_2_right"])};_

#### **_\#C34: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_2"] / [label=="north_2_front"] > -> roundShape("front", "outside", 0.3, 30, "main_back", "vertical")};_

#### **_\#C35: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (8, 9, 10)] [::groupRegions()] > -> addVolume("north_3", "building_back", 1, ["north_3_front", "north_3_left", "north_3_right"])};_

#### **_\#C36: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_3"] / [label=="north_3_front"] > -> roundShape("right", "inside", 0.4, 30, "main_back", 0.05)};_

#### **_\#C37: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (11, 12, 13)] [::groupRegions()] > -> addVolume("north_4", "building_back", 1, ["north_4_front", "north_4_left", "north_4_right"])};_

#### **_\#C38: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_4"] / [label=="north_4_front"] > -> roundShape("left", "inside", 0.4, 30, "main_back", 0.05)};_

#### **_\#C39: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (14, 15, 16, 17, 18, 19)] [::groupRegions()] > -> addVolume("north_5", "building_back", 3, ["north_5_front", "north_5_left", "north_5_right"])};_

#### **_\#C40: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_5"] / [label=="north_5_front"] > -> roundShape("front", "outside", 0.3, 30, "main_back", "vertical")};_

#### **_\#C41: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5)] [colIdx in (20)] [::groupRegions()] > -> addVolume("north_6", "building_back", 1, ["north_6_front", "north_6_left", "north_6_right"])};_

#### **_\#C42: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_6"] / [label=="north_6_front"] > -> roundShape("right", "inside", 0.4, 30, "main_back", 0.05)};_

---

<h2 align="center">🏢 Resultado</h2>

<div align="center">
  <img src="modelo_11.png" alt="Modelo 11">
</div>
