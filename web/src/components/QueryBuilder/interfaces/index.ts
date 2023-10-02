export interface IQuerBuilderRequest {
  id: string;
  filter: IFilter;
  onAdd: Function;
  onUpdate: Function;
  onDelete: Function;
}

export interface IFilter {
  id: string;
  lhs: IExpression | undefined;
  op: IOp;
  rhs: IExpression | undefined;
  filters: IFilter[];
}

export interface IExpression {
  columnIdentifier?: IColumnIdentifier | undefined;
  attributeIdentifier?: IAttributeIdentifier | undefined;
  literal?: ILiteral | undefined;
}

export interface ILiteral {
  literalType: ILiteralType;
  string: string | undefined;
  long: number | undefined;
  double: number | undefined;
  boolean: boolean | undefined;
  timestamp: number;
  id: IdLiteral | undefined;
  stringArray: string[];
  longArray: number[];
  doubleArray: number[];
  bytesArray: Uint8Array[];
  booleanArray: boolean[];
  idArray: IdLiteral[];
}

export interface IColumnIdentifier {
  name: string;
}

export interface IAttributeIdentifier {
  name: string;
  path: string;
}

export enum IOp {
  UNKNOWN_OP = 0,
  EQ = 1,
  NEQ = 2,
  GT = 3,
  LT = 4,
  GTE = 5,
  LTE = 6,
  IN = 7,
  NOT_IN = 8,
  LIKE = 9,
  IS_NULL = 10,
  EXISTS = 11,
  AND = 20,
  OR = 21,
  NOT = 22,
  UNRECOGNIZED = -1
}

export enum ILiteralType {
  UNKNOWN_LT = 0,
  STRING = 1,
  LONG = 2,
  DOUBLE = 3,
  BOOLEAN = 4,
  TIMESTAMP = 5,
  ID = 6,
  STRING_ARRAY = 7,
  LONG_ARRAY = 8,
  DOUBLE_ARRAY = 9,
  BOOLEAN_ARRAY = 10,
  ID_ARRAY = 12,
  NULL_STRING = 13,
  NULL_NUMBER = 14,
  UNRECOGNIZED = -1
}

export interface IdLiteral {
  type: IdLiteral_Type;
  long?: number | undefined;
  string?: string | undefined;
}

export enum IdLiteral_Type {
  UNKNOWN = 0,
  LONG = 1,
  STRING = 2,
  UNRECOGNIZED = -1
}
