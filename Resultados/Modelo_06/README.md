<h1 align="center">Modelo 06</h2>

<h2 align="center">📝 rules_6.slx</h2>

#### **_\#C1: Initial settings_**

_label = "building"; width = 20; depth = 10; height = 10;_

#### **_\#C2: Generating mass model_**

_{<> -> createShape("building", width, depth, height)};_

\# GRIDS:

#### **_\#C3: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_front"] > -> createGrid("main_front_grid", 20, 13)};_

#### **_\#C4: Adding virtual shape to the mass model_**

_{< descendant() [label=="building"] / [label=="building_right"] > -> createGrid("main_right_grid", 20, 10)};_

\# FRONT DEFORMATION:

#### **_\#C5: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)] [colIdx in (1, 2, 3, 4)] [::groupRegions()] > -> addVolume("south_1", "building_front", 6, ["south_1_front", "south_1_left", "south_1_right"])};_

#### **_\#C6: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_1"] / [label=="south_1_front"] > -> roundShape("front", "outside", 0.21, 30, "main_front", "vertical")};_

#### **_\#C7: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)] [colIdx in (9, 10, 11, 12)] [::groupRegions()] > -> addVolume("south_2", "building_front", 6, ["south_2_front", "south_2_left", "south_2_right"])};_

#### **_\#C8: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_2"] / [label=="south_2_front"] > -> roundShape("front", "outside", 0.21, 30, "main_front", "vertical")};_

#### **_\#C9: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)] [colIdx in (13)] [::groupRegions()] > -> addVolume("south_3", "building_front", 2, ["south_3_front", "south_3_left", "south_3_right"])};_

#### **_\#C10: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_3"] / [label=="south_3_front"] > -> roundShape("right", "outside", 0.2, 30, "main_front")};_

#### **_\#C11: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (17, 18, 19, 20)] [colIdx in (5, 6, 7, 8)] [::groupRegions()] > -> addVolume("south_4", "building_front", 4, ["south_4_front", "south_4_left", "south_4_right"])};_

#### **_\#C12: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_4"] / [label=="south_4_front"] > -> roundShape("top", "outside", 0.2, 30, "main_front")};_

#### **_\#C13: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="main_front_grid"] / [type=="cell"] [rowIdx in (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)] [colIdx in (5, 6, 7, 8)] ::groupRegions()] > -> addVolume("south_5", "building_front", 2, ["south_5_front", "south_5_left", "south_5_right"])};_

#### **_\#C14: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_front"] / [label=="south_5"] / [label=="south_5_front"] > -> roundShape("top", "outside", 0.2, 30, "main_front")};_

\# RIGHT DEFORMATION:

#### **_\#C15: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (15, 16, 17, 18, 19, 20)] [colIdx in (1)] [::groupRegions()] > -> addVolume("east_1", "building_right", 2, ["east_1_front", "east_1_left", "east_1_right"])};_

#### **_\#C16: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_1"] / [label=="east_1_front"] > -> roundShape("front", "outside", 0.09, 30, "main_right", "vertical")};_

#### **_\#C17: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (15, 16, 17, 18, 19, 20)] [colIdx in (10)] [::groupRegions()] > -> addVolume("east_2", "building_right", 2, ["east_2_front", "east_2_left", "east_2_right"])};_

#### **_\#C18: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_2"] / [label=="east_2_front"] > -> roundShape("front", "outside", 0.09, 30, "main_right", "vertical")};_

#### **_\#C19: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)] [colIdx in (1)] [::groupRegions()] > -> addVolume("east_3", "building_right", 1.5, ["east_3_front", "east_3_left", "east_3_right"])};_

#### **_\#C20: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_3"] / [label=="east_3_front"] > -> roundShape("left", "outside", 0.2, 30, "main_right")};_

#### **_\#C21: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)] [colIdx in (10)] [::groupRegions()] > -> addVolume("east_4", "building_right", 1.5, ["east_4_front", "east_4_left", "east_4_right"])};_

#### **_\#C22: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_4"] / [label=="east_4_front"] > -> roundShape("right", "outside", 0.2, 30, "main_right")};_

#### **_\#C23: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (13, 14)] [colIdx in (2, 3, 4, 5, 6, 7, 8, 9)] [::groupRegions()] > -> addVolume("east_5", "building_right", 1.5, ["east_5_front", "east_5_left", "east_5_right"])};_

#### **_\#C24: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_5"] / [label=="east_5_front"] > -> roundShape("top", "outside", 0.2, 30, "main_right")};_

#### **_\#C25: Selecting region and performing extrusion_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="main_right_grid"] / [type=="cell"] [rowIdx in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12)] [colIdx in (2, 3, 4, 5, 6, 7, 8, 9)] [::groupRegions()] > -> addVolume("east_6", "building_right", 1.5, ["east_6_front", "east_6_left", "east_6_right"])};_

#### **_\#C26: Applying roundShape deformation_**

_{< descendant() [label=="building"] / [label=="building_right"] / [label=="east_6"] / [label=="east_6_front"] > -> roundShape("front", "outside", 0.3, 30, "main_right", "horizontal")};_

---

<h2 align="center">🏢 Resultado</h2>

<div align="center">
  <img src="modelo_06.png" alt="Modelo 06">
</div>
