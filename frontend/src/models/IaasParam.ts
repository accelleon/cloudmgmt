/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type IaasParam = {
    key: string;
    label: string;
    type?: IaasParam.type;
    choices?: Array<string>;
    readonly?: boolean;
};

export namespace IaasParam {

    export enum type {
        STRING = 'string',
        CHOICE = 'choice',
        SECRET = 'secret',
    }


}
