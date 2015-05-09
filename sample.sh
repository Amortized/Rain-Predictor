header=$(head -n 1 data/train_preprocessed.csv);
sed -e '1d' data/train_preprocessed.csv > data/train_preprocessed_.csv;
mv data/train_preprocessed_.csv data/train_preprocessed.csv; 
shuf data/train_preprocessed.csv > data/train_preprocessed_shuffled.csv;
no_lines=$(sed -n '$=' data/train_preprocessed_shuffled.csv);
val_set_size=0.60;
val_size=$(echo $no_lines*$val_set_size | bc );
val_size=$( printf "%.0f" $val_size )
train_size=$(echo $no_lines - $val_size | bc );
echo $header > data/training_set.csv;
echo $header > data/validation_set.csv;
head -n $train_size data/train_preprocessed_shuffled.csv >> data/training_set.csv;
tail -n $val_size data/train_preprocessed_shuffled.csv >> data/validation_set.csv;
rm data/train_preprocessed_shuffled.csv;
