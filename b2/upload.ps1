# I'm not the author of this script (I don't think).
# One probably needs to have some ENVARS in place
# before this script will work.

#Make sure PS doesn't trip over non-american letters
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

#Pick up all items from src folder.
$parallelJob = Get-Childitem -Path "$srcdir\*" -Recurse | Where-Object { ! $_.PSIsContainer }

#Start parallel upload
$parallelJob.Fullname | ForEach-Object -Parallel {

  #The Parallel for each hard scoped, that's why Vars are here and not globally set.
  $bucket = "B2BUCKETNAME"
  $srcdir = "C:\Users\USER\Desktop\Backblaze\"
  $dest = "DST/DIR"

  #The $_ object risks to be overwritten by an Error. 
  #Therefore we'll place the content of the Object in another var called srcFile
  $srcFile = $_
  #Substring the Path to the local folder
  $bucketPath = $srcFile.substring(39)
  #Store File Name
  $fileName = $srcFile.split("\")[-1]

  #Substring can throw errors when no pathing is, we handle this with Try Catch.
  #Upload files as per b2 upload-file description.
  #The Substring ($bucketPath.substring(0,$bucketPath.length-$fileName.length-1) removes the filename and the last '/'.
  #The .replace('\','/') corrects any wrongly set slashes (derived from Windows path)
  #The .replace('//','/') handles any double slashes ('//') that might occur.
  try {
    b2 upload-file $bucket $srcFile ("$($dest)/$(($bucketPath.substring(0,$bucketPath.length-$fileName.length-1)).replace('\','/'))/$($fileName)").replace('//','/') --quiet --noProgress
  }
  catch {
    b2 upload-file $bucket $srcFile ("$($dest)/$($fileName)").replace('//','/') --quiet --noProgress
  }
} -ThrottleLimit 5