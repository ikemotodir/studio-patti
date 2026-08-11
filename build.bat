@echo off
rem Patti.aseprite から patti.png + patti.json を書き出し直す
cd /d "%~dp0"
set ASE="C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe"
%ASE% -b "..\Patti.aseprite" --sheet "patti.png" --sheet-type horizontal --data "patti.json" --format json-array --list-tags
rem 部屋（make_room.py が正。room_layers\ とジュークボックスの点滅コマも一緒に書き出す）
rem   ※手で描き直したい時は web\overrides\ に furniture.png などを置けば最優先で上に乗る
python make_room.py
rem パッチくんに陰影を乗せる（原本はいじらない）
python shade_patti.py
rem マユちゃん（Mayu.aseprite → シート+JSON → 夜トーン）
%ASE% -b "..\..\Mayu\Mayu.aseprite" --sheet "mayu.png" --sheet-type horizontal --data "mayu.json" --format json-array --list-tags
python shade_mayu.py
rem 月のおばけボンボン（Bonbon.aseprite → シート → 月あかりトーン）
%ASE% -b "..\..\Bonbon\Bonbon.aseprite" --sheet "bonbon.png" --sheet-type horizontal --data "bonbon.json" --format json-array --list-tags
python shade_bonbon.py
rem UI用のドット絵（スマホを横にしてね のアニメ）
python make_ui.py
rem 重い素材（ブラウン管の動画・設計図の写真）をWeb用の軽さに落とす
python prep_media.py
rem ギャラリー（サイト用画像\gallery の原画をWeb用に最適化して取り込む）
python prep_gallery.py
rem 絵本の高画質スキャンを取り込む
python prep_book.py
rem 寄りの画面（closeup_*.png と矩形データ closeups.json）
python make_closeups.py
echo.
echo 書き出し完了。start.bat でブラウザを開くと反映されています。
pause
