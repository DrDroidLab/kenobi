export const addToLocalArray = (arrayName, element) => {
  let array = getLocalArray(arrayName);
  array.push(element);
  localStorage.setItem(arrayName, JSON.stringify(array));
};

export const getLocalArray = arrayName => {
  if (localStorage.getItem(arrayName) === null) {
    localStorage.setItem(arrayName, JSON.stringify([]));
  }
  return JSON.parse(localStorage.getItem(arrayName));
};
