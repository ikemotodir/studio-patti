local I = {}
I[1] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/bg.png" }
I[2] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__005_キャラクターデザインと設計の紙.png" }
I[3] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__007_おばけのラフ絵.png" }
I[4] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__009_Story is Kingの紙.png" }
I[5] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__011_Spooks GSの紙.png" }
I[6] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__012_世界観の紙.png" }
I[7] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__014_物語の紙.png" }
I[8] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__017_キャラクターに関するデータ.png" }
I[9] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__019_スタジオへの戸口.png" }
I[10] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__020_スタジオの看板.png" }
I[11] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__021_ガーランド.png" }
I[12] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/furniture__022_チョーク受け.png" }
I[13] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/props__006_キャラクターデザインと設計の紙.png" }
I[14] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/props__008_おばけのラフ絵.png" }
I[15] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/props__010_Story is Kingの紙.png" }
I[16] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/props__013_世界観の紙.png" }
I[17] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/props__015_物語の紙.png" }
I[18] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/props__018_キャラクターに関するデータ.png" }
I[19] = Image{ fromFile = "/home/runner/work/studio-patti/studio-patti/room_design_layers/objects/props__024_チョーク.png" }
local spr = Sprite(384, 240, ColorMode.RGB)
spr:deleteLayer(spr.layers[1])
do
  local l = spr:newLayer()
  l.name = "bg"
  spr:newCel(l, 1, I[1], Point(0, 0))
end
do
  local g = spr:newGroup()
  g.name = "furniture"
  g.isCollapsed = true
  do
    local l = spr:newLayer()
    l.name = "キャラクターデザインと設計の紙"
    l.parent = g
    spr:newCel(l, 1, I[2], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "おばけのラフ絵"
    l.parent = g
    spr:newCel(l, 1, I[3], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "Story is Kingの紙"
    l.parent = g
    spr:newCel(l, 1, I[4], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "Spooks GSの紙"
    l.parent = g
    spr:newCel(l, 1, I[5], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "世界観の紙"
    l.parent = g
    spr:newCel(l, 1, I[6], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "物語の紙"
    l.parent = g
    spr:newCel(l, 1, I[7], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "キャラクターに関するデータ"
    l.parent = g
    spr:newCel(l, 1, I[8], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "スタジオへの戸口"
    l.parent = g
    spr:newCel(l, 1, I[9], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "スタジオの看板"
    l.parent = g
    spr:newCel(l, 1, I[10], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "ガーランド"
    l.parent = g
    spr:newCel(l, 1, I[11], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "チョーク受け"
    l.parent = g
    spr:newCel(l, 1, I[12], Point(0, 0))
  end
end
do
  local g = spr:newGroup()
  g.name = "props"
  g.isCollapsed = true
  do
    local l = spr:newLayer()
    l.name = "キャラクターデザインと設計の紙"
    l.parent = g
    spr:newCel(l, 1, I[13], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "おばけのラフ絵"
    l.parent = g
    spr:newCel(l, 1, I[14], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "Story is Kingの紙"
    l.parent = g
    spr:newCel(l, 1, I[15], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "世界観の紙"
    l.parent = g
    spr:newCel(l, 1, I[16], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "物語の紙"
    l.parent = g
    spr:newCel(l, 1, I[17], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "キャラクターに関するデータ"
    l.parent = g
    spr:newCel(l, 1, I[18], Point(0, 0))
  end
  do
    local l = spr:newLayer()
    l.name = "チョーク"
    l.parent = g
    spr:newCel(l, 1, I[19], Point(0, 0))
  end
end
spr:saveAs("/home/runner/work/studio-patti/studio-patti/room_design.aseprite")
print("aseprite written: " .. tostring(#spr.layers) .. " top-level layers")
