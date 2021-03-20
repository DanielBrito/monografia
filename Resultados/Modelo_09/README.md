<h1 align="center">Modelo 09</h2>

<h2 align="center">📝 rules_9.slx</h2>

#### **_\#C1: Initial settings_**

_label = "building"; width = 3; depth = 3; height = 9;_

#### **_\#C2: Generating mass model_**

_{<> -> createShape(label, width, depth, height)};_

\# GRIDS:

#### **_\#C3: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_front"] > -> createGrid("main_front_grid", 9, 3)};_

#### **_\#C4: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_back"] > -> createGrid("main_back_grid", 9, 3)};_

#### **_\#C5: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_left"] > -> createGrid("main_left_grid", 9, 3)};_

#### **_\#C6: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_right"] > -> createGrid("main_right_grid", 9, 3)};_

\# FRONT:

#### **_\#C7: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (7, 8, 9)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("south_1", "building_front", 4, ["south_1_front", "south_1_left", "south_1_right"])};_

#### **_\#C8: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_1"] / [label=="south_1_front"] > -> roundShape("top", "outside", 0.5, 30, "main_front", "vertical")};_

#### **_\#C9: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (4, 5, 6)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("south_2", "building_front", 2.5, ["south_2_front", "south_2_left", "south_2_right"])};_

#### **_\#C10: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_2"] / [label=="south_2_front"] > -> roundShape("top", "outside", 0.5, 30, "main_front", "vertical")};_

#### **_\#C11: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (1, 2, 3)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("south_3", "building_front", 1, ["south_3_front", "south_3_left", "south_3_right"])};_

#### **_\#C12: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_3"] / [label=="south_3_front"] > -> roundShape("top", "outside", 0.5, 30, "main_front", "vertical")};_

\# LEFT:

#### **_\#C13: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="main_left_grid"] / [type=="cell"] [rowIdx in (7, 8, 9)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("west_1", "building_left", 4, ["west_1_front", "west_1_left", "west_1_right"])};_

#### **_\#C14: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="west_1"] / [label=="west_1_front"] > -> roundShape("top", "outside", 0.5, 30, "main_left", "vertical")};_

#### **_\#C15: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="main_left_grid"] / [type=="cell"] [rowIdx in (4, 5, 6)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("west_2", "building_left", 2.5, ["west_2_front", "west_2_left", "west_2_right"])};_

#### **_\#C16: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="west_2"] / [label=="west_2_front"] > -> roundShape("top", "outside", 0.5, 30, "main_left", "vertical")};_

#### **_\#C17: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="main_left_grid"] / [type=="cell"] [rowIdx in (1, 2, 3)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("west_3", "building_left", 1, ["west_3_front", "west_3_left", "west_3_right"])};_

#### **_\#C18: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_left"] / [label=="west_3"] / [label=="west_3_front"] > -> roundShape("top", "outside", 0.5, 30, "main_left", "vertical")};_

\# RIGHT:

#### **_\#C19: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (7, 8, 9)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("east_1", "building_right", 4, ["east_1_front", "east_1_left", "east_1_right"])};_

#### **_\#C20: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_1"] / [label=="east_1_front"] > -> roundShape("top", "outside", 0.5, 30, "main_right", "vertical")};_

#### **_\#C21: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (4, 5, 6)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("east_2", "building_right", 2.5, ["east_2_front", "east_2_left", "east_2_right"])};_

#### **_\#C22: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_2"] / [label=="east_2_front"] > -> roundShape("top", "outside", 0.5, 30, "main_right", "vertical")};_

#### **_\#C23: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (1, 2, 3)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("east_3", "building_right", 1, ["east_3_front", "east_3_left", "east_3_right"])};_

#### **_\#C24: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_3"] / [label=="east_3_front"] > -> roundShape("top", "outside", 0.5, 30, "main_right", "vertical")};_

\# BACK:

#### **_\#C25: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (7, 8, 9)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("north_1", "building_back", 4, ["north_1_front", "north_1_left", "north_1_right"])};_

#### **_\#C26: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_1"] / [label=="north_1_front"] > -> roundShape("top", "outside", 0.5, 30, "main_back", "vertical")};_

#### **_\#C27: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (4, 5, 6)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("north_2", "building_back", 2.5, ["north_2_front", "north_2_left", "north_2_right"])};_

#### **_\#C28: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_2"] / [label=="north_2_front"] > -> roundShape("top", "outside", 0.5, 30, "main_back", "vertical")};_

#### **_\#C29: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="main_back_grid"] / [type=="cell"] [rowIdx in (1, 2, 3)] [colIdx in (1, 2, 3)] [::groupRegions()] > -> addVolume("north_3", "building_back", 1, ["north_3_front", "north_3_left", "north_3_right"])};_

#### **_\#C30: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_back"] / [label=="north_3"] / [label=="north_3_front"] > -> roundShape("top", "outside", 0.5, 30, "main_back", "vertical")};_

---

<h2 align="center">🏢 Resultado</h2>

<div align="center">
  <img src="modelo_09.png" alt="Modelo 09">
</div>
