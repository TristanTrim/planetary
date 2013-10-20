FILES=gifs/*
for f in $FILES
do
echo "$f"
mkdir "images/$f"
convert gif:"$f" "images/$f/%d.gif"
done
