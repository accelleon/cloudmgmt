<template>
    <q-layout view="lHh Lpr lFf" class="img-background">
        <q-page-container class="container-fluid">
            <router-view />
        </q-page-container>
    </q-layout>
</template>

<style scoped>
::-webkit-scrollbar {
    display: none;
}
.img-background {
    background: #fff;
    height: 100%;
}
</style>