if type == "object" and (.jobs | type) == "array" then
  .jobs
elif type == "array" then
  .
else
  error("unexpected Actions jobs API envelope")
end
| if all(.[]; type == "object") then
    .
  else
    error("Actions jobs API entries must be objects")
  end
