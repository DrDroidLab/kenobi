import { randomString } from '../utils/utils';

const useNode = () => {
  const deleteNode = ({ tree, id, isGroup }) => {
    for (let i = 0; i < tree?.filters?.length; i++) {
      const currentFilter = tree?.filters?.[i];
      if (currentFilter.id === id) {
        tree.filters.splice(i, 1);
        return tree;
      } else {
        deleteNode({ tree: currentFilter, id, isGroup });
      }
    }
    return { ...tree };
  };

  const updateNode = ({ tree, id, value, type, isGroup }: any) => {
    if (tree.id === id) {
      tree[type] = value;
      return tree;
    }
    let latestNode = [];
    latestNode = tree?.filters?.map(filter => {
      if (filter?.filters?.length > 0 && filter?.op !== 'NOT') {
        return updateNode({ tree: filter, id, value, type, isGroup: true });
      }
      return updateNode({ tree: filter, id, value, type });
    });
    return { ...tree, filters: latestNode };
  };

  const insertNode = ({ tree, id, isGroup }) => {
    let newNode;
    if (isGroup) {
      newNode = {
        id: randomString(),
        op: 'AND',
        filters: []
      };
    } else {
      newNode = {
        id: randomString(),
        path: '',
        optionType: '',
        lhs: '',
        lhsType: '',
        op: '',
        operators: [],
        rhs: '',
        rhsType: '',
        rhsOptions: []
      };
    }
    if (tree.id === id) {
      tree.filters.push(newNode);
      return tree;
    }
    let latestNode = [];
    latestNode = tree?.filters?.map(filter => {
      return insertNode({ tree: filter, id, isGroup });
    });
    return { ...tree, filters: latestNode };
  };

  return {
    insertNode,
    deleteNode,
    updateNode
  };
};
export default useNode;
